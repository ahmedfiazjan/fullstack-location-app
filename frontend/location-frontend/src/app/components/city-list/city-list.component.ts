import { Component, OnInit, Input, Output, EventEmitter, SimpleChanges, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { LocationService } from '../../services/location.service';
import { Subject, Subscription } from 'rxjs';
import { debounceTime, distinctUntilChanged } from 'rxjs/operators';

@Component({
  selector: 'app-city-list',
  templateUrl: './city-list.component.html',
  styleUrls: ['./city-list.component.scss'],
  standalone: true,
  imports: [CommonModule, FormsModule]
})
export class CityListComponent implements OnInit, OnDestroy {
  @Input() selectedStateId?: number;
  @Output() citySelected = new EventEmitter<any>();

  cities: any[] = [];
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
      this.loadCities(searchTerm);
    });
  }

  ngOnInit(): void {
    if (this.selectedStateId) {
      this.loadCities();
    }
  }

  ngOnDestroy(): void {
    if (this.searchSubscription) {
      this.searchSubscription.unsubscribe();
    }
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['selectedStateId'] && !changes['selectedStateId'].firstChange) {
      this.currentPage = 1;
      this.searchTerm = '';
      this.loadCities();
    }
  }

  onSearch(value: string): void {
    this.searchTerm = value;
    this.searchSubject.next(value);
  }

  loadCities(search?: string): void {
    if (!this.selectedStateId) return;

    const searchQuery = search !== undefined ? search : this.searchTerm;

    this.locationService.getCities(this.selectedStateId, searchQuery, this.currentPage).subscribe({
      next: (response) => {
        this.cities = response.results;
        this.totalPages = Math.ceil(response.count / 10);
      },
      error: (error) => {
        console.error('Error loading cities:', error);
        this.cities = [];
        this.totalPages = 1;
      }
    });
  }

  onCitySelect(city: any): void {
    this.citySelected.emit(city);
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
      this.loadCities();
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadCities();
    }
  }
}
