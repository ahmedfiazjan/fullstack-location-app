import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { CountryListComponent } from '../country-list/country-list.component';
import { StateListComponent } from '../state-list/state-list.component';
import { CityListComponent } from '../city-list/city-list.component';
import { ZipcodeListComponent } from '../zipcode-list/zipcode-list.component';

@Component({
  selector: 'app-location-layout',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    CountryListComponent,
    StateListComponent,
    CityListComponent,
    ZipcodeListComponent
  ],
  template: `
    <div class="app-container">
      <div class="lists-container">
        <app-country-list
          (countrySelected)="onCountrySelect($event)"
        ></app-country-list>

        <app-state-list
          *ngIf="selectedCountry"
          [selectedCountryId]="selectedCountry.id"
          (stateSelected)="onStateSelect($event)"
        ></app-state-list>

        <app-city-list
          *ngIf="selectedState"
          [selectedStateId]="selectedState.id"
          (citySelected)="onCitySelect($event)"
        ></app-city-list>

        <app-zipcode-list
          *ngIf="selectedCity"
          [selectedCity]="selectedCity"
        ></app-zipcode-list>
      </div>
    </div>
  `,
  styles: [`
    .app-container {
      padding: 20px;
    }
    .lists-container {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin: 0 auto;
      max-width: 1400px;
    }
  `]
})
export class LocationLayoutComponent {
  selectedCountry: any;
  selectedState: any;
  selectedCity: any;

  onCountrySelect(country: any): void {
    this.selectedCountry = country;
    this.selectedState = null;
    this.selectedCity = null;
  }

  onStateSelect(state: any): void {
    this.selectedState = state;
    this.selectedCity = null;
  }

  onCitySelect(city: any): void {
    this.selectedCity = city;
  }
}
