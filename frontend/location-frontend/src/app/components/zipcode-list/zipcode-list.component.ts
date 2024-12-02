import { Component, OnInit, Input, OnDestroy, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LocationService } from '../../services/location.service';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

@Component({
  selector: 'app-zipcode-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container">
      <h2>Zip Codes for {{ selectedCity?.name }}</h2>

      <div class="search-box">
        <input
          type="text"
          [ngModel]="searchTerm"
          (ngModelChange)="onSearch($event)"
          placeholder="Search zip codes..."
          class="search-input"
        >
      </div>

      <div class="list-container">
        <div *ngFor="let zipcode of zipcodes" class="list-item">
          {{ zipcode.zip_code }}
        </div>
      </div>

      <div class="pagination">
        <button
          (click)="previousPage()"
          [disabled]="currentPage === 1"
          class="pagination-button"
        >
          Previous
        </button>
        <span>Page {{ currentPage }} of {{ totalPages }}</span>
        <button
          (click)="nextPage()"
          [disabled]="currentPage === totalPages"
          class="pagination-button"
        >
          Next
        </button>
      </div>
    </div>
  `,
  styles: [`
    .container {
      padding: 1rem;
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .search-box {
      margin-bottom: 1rem;

      .search-input {
        width: 100%;
        padding: 0.5rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        font-size: 1rem;

        &:focus {
          outline: none;
          border-color: #007bff;
        }
      }
    }

    .list-container {
      margin-bottom: 1rem;

      .list-item {
        padding: 0.75rem;
        border-bottom: 1px solid #eee;
        cursor: pointer;
        transition: background-color 0.2s;

        &:hover {
          background-color: #f8f9fa;
        }

        &:last-child {
          border-bottom: none;
        }
      }
    }

    .pagination {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 1rem;
      border-top: 1px solid #eee;

      .pagination-button {
        padding: 0.5rem 1rem;
        border: 1px solid #ddd;
        border-radius: 4px;
        background: white;
        cursor: pointer;

        &:disabled {
          background: #f5f5f5;
          cursor: not-allowed;
        }

        &:not(:disabled):hover {
          background: #f8f9fa;
        }
      }
    }
  `]
})
export class ZipcodeListComponent implements OnInit, OnDestroy {
  @Input() selectedCity?: any;

  zipcodes: any[] = [];
  searchTerm = '';
  currentPage = 1;
  totalPages = 1;
  private searchSubject = new Subject<string>();
  private searchSubscription?: Subscription;

  constructor(private locationService: LocationService) {
    this.setupSearchSubscription();
  }

  private setupSearchSubscription(): void {
    this.searchSubscription = this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged()
    ).subscribe(searchTerm => {
      this.currentPage = 1;
      this.loadZipCodes(searchTerm);
    });
  }

  ngOnInit(): void {
    if (this.selectedCity) {
      this.loadZipCodes();
    }
  }

  ngOnDestroy(): void {
    if (this.searchSubscription) {
      this.searchSubscription.unsubscribe();
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['selectedCity'] && !changes['selectedCity'].firstChange) {
      this.currentPage = 1;
      this.searchTerm = '';
      this.loadZipCodes();
    }
  }

  onSearch(value: string): void {
    this.searchTerm = value;
    this.searchSubject.next(value);
  }

  loadZipCodes(search?: string): void {
    if (!this.selectedCity?.name) return;

    const searchQuery = search !== undefined ? search : this.searchTerm;

    this.locationService.getZipCodes(this.selectedCity.name, searchQuery, this.currentPage).subscribe({
      next: (response) => {
        this.zipcodes = response.results;
        this.totalPages = Math.ceil(response.count / 10);
      },
      error: (error) => {
        console.error('Error loading zip codes:', error);
        this.zipcodes = [];
        this.totalPages = 1;
      }
    });
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadZipCodes();
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadZipCodes();
    }
  }
}
