import { Component, OnInit, Input, Output, EventEmitter, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LocationService } from '../../services/location.service';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

@Component({
  selector: 'app-state-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container">
      <h2>States</h2>

      <div class="search-box">
        <input
          type="text"
          [(ngModel)]="searchTerm"
          (input)="onSearch($event)"
          placeholder="Search states..."
          class="search-input"
        >
      </div>

      <div class="list-container">
        <div *ngFor="let state of states"
             class="list-item"
             (click)="onStateSelect(state)">
          {{ state.name }}
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
  `
})
export class StateListComponent implements OnInit {
  @Input() selectedCountryId?: number;
  @Output() stateSelected = new EventEmitter<any>();

  states: any[] = [];
  searchTerm = '';
  currentPage = 1;
  totalPages = 1;
  private searchSubject = new Subject<string>();

  constructor(private locationService: LocationService) {
    this.searchSubject.pipe(
      debounceTime(300),
      distinctUntilChanged()
    ).subscribe(searchTerm => {
      this.currentPage = 1;
      this.loadStates(searchTerm);
    });
  }

  ngOnInit(): void {
    if (this.selectedCountryId) {
      this.loadStates();
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['selectedCountryId'] && !changes['selectedCountryId'].firstChange) {
      this.currentPage = 1;
      this.searchTerm = '';
      this.loadStates();
    }
  }

  onSearch(event: any): void {
    this.searchSubject.next(event.target.value);
  }

  loadStates(search?: string): void {
    if (!this.selectedCountryId) return;

    this.locationService.getStates(this.selectedCountryId, search, this.currentPage).subscribe({
      next: (response) => {
        this.states = response.results;
        this.totalPages = Math.ceil(response.count / 10);
      },
      error: (error) => console.error('Error loading states:', error)
    });
  }

  onStateSelect(state: any): void {
    this.stateSelected.emit(state);
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadStates(this.searchTerm);
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadStates(this.searchTerm);
    }
  }
}
