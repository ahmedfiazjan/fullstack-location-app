import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LocationService } from '../../services/location.service';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

@Component({
  selector: 'app-country-list',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container">
      <h2>Countries</h2>

      <div class="search-box">
        <input
          type="text"
          [(ngModel)]="searchTerm"
          (input)="onSearch($event)"
          placeholder="Search countries..."
          class="search-input"
        >
      </div>

      <div class="list-container">
        <div *ngFor="let country of countries"
             class="list-item"
             (click)="onCountrySelect(country)">
          {{ country.name }}
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
export class CountryListComponent implements OnInit {
  @Output() countrySelected = new EventEmitter<any>();

  countries: any[] = [];
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
      this.loadCountries(searchTerm);
    });
  }

  ngOnInit(): void {
    this.loadCountries();
  }

  onSearch(event: any): void {
    this.searchSubject.next(event.target.value);
  }

  onCountrySelect(country: any): void {
    this.countrySelected.emit(country);
  }

  loadCountries(search?: string): void {
    this.locationService.getCountries(search, this.currentPage).subscribe({
      next: (response) => {
        this.countries = response.results;
        this.totalPages = Math.ceil(response.count / 10);
      },
      error: (error) => console.error('Error loading countries:', error)
    });
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadCountries(this.searchTerm);
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadCountries(this.searchTerm);
    }
  }
}
