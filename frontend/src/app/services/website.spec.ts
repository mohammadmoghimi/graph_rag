import { TestBed } from '@angular/core/testing';

import { Website } from './website';

describe('Website', () => {
  let service: Website;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(Website);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
