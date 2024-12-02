import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class LocationService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  getCountries(search?: string, page: number = 1): Observable<any> {
    let params = new HttpParams().set('page', page.toString());
    if (search) {
      params = params.set('search', search);
    }
    return this.http.get(`${this.baseUrl}/countries/`, { params });
  }

  getStates(countryId?: number, search?: string, page: number = 1): Observable<any> {
    let params = new HttpParams().set('page', page.toString());
    if (search) {
      params = params.set('search', search);
    }
    if (countryId) {
      params = params.set('country', countryId.toString());
    }
    return this.http.get(`${this.baseUrl}/states/`, { params });
  }

  getCities(stateId?: number, search?: string, page: number = 1): Observable<any> {
    let params = new HttpParams().set('page', page.toString());
    if (search) {
      params = params.set('search', search);
    }
    if (stateId) {
      params = params.set('state', stateId.toString());
    }
    return this.http.get(`${this.baseUrl}/cities/`, { params });
  }

  getZipCodes(cityName?: string, search?: string, page: number = 1): Observable<any> {
    let params = new HttpParams().set('page', page.toString());
    if (search) {
      params = params.set('search', search);
    }
    if (cityName) {
      params = params.set('city', cityName);
    }
    return this.http.get(`${this.baseUrl}/zipcodes/`, { params });
  }
}
