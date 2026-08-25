import { Component, OnInit } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { WebsiteService } from '../../services/website';

@Component({
  selector: 'app-websites',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './websites.html',
  styleUrl: './websites.scss'
})
export class Websites implements OnInit {
  isCrawling = false;
  errorMessage = '';
  successMessage = '';
  websiteForm!: FormGroup;

  constructor(
    private formBuilder: FormBuilder,
    private websiteService: WebsiteService
  ) {}

  ngOnInit(): void {
    this.websiteForm = this.formBuilder.group({
      name: ['', Validators.required],
      url: ['', [Validators.required, Validators.pattern(/^https?:\/\/.+/)]],
      description: ['']
    });
  }

  submit() {
    console.log('SUBMIT');
    if (this.websiteForm.invalid || this.isCrawling) {
      this.websiteForm.markAllAsTouched();
      return;
    }

    const { name, url, description } = this.websiteForm.getRawValue();

    this.isCrawling = true;
    this.errorMessage = '';
    this.successMessage = '';

    console.log('SENDING REQUEST');
    this.websiteService
      .crawlWebsite(name!, url!, description || '')
      .subscribe({
        next: response => {
          this.isCrawling = false;
          this.successMessage =
            `وب‌سایت با موفقیت پردازش شد. ${response.crawl.pages_processed} صفحه پردازش شد.`;

          this.websiteForm.reset();
        },
        error: error => {
          this.isCrawling = false;
          this.errorMessage =
            error.error?.error || 'خطا در پردازش وب‌سایت.';
        }
      });
  }
}