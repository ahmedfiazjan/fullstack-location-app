import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ZipcodeListComponent } from './zipcode-list.component';

describe('ZipcodeListComponent', () => {
  let component: ZipcodeListComponent;
  let fixture: ComponentFixture<ZipcodeListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ZipcodeListComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ZipcodeListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
