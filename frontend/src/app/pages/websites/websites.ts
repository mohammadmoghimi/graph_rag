import { ChatService } from './../../services/chat';
import { Component, OnInit } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { Website, WebsiteService } from '../../services/website';
import { Router } from '@angular/router';

@Component({
  selector: 'app-websites',
  standalone: true,
  imports: [ReactiveFormsModule],
  templateUrl: './websites.html',
  styleUrl: './websites.scss'
})
export class Websites implements OnInit {

  websiteForm!: FormGroup;
  websites: Website[] = [];
  isCrawling = false;
  isLoading = true;
  errorMessage = '';
  successMessage = '';

  constructor(
    private formBuilder: FormBuilder,
    private websiteService: WebsiteService,
    private chatService : ChatService,
    private router : Router
  ) {}

  ngOnInit() {
    this.websiteForm = this.formBuilder.group({
      name: ['', Validators.required],
      url: ['', [Validators.required, Validators.pattern(/^https?:\/\/.+/)]],
      description: ['']
    });

    this.loadWebsites();
  }

  submit() {
    if (this.websiteForm.invalid || this.isCrawling) {
      this.websiteForm.markAllAsTouched();
      return;
    }

    const { name, url, description } = this.websiteForm.getRawValue();
    this.processCrawl(name, url, description || '');
  }

  private loadWebsites() {
    this.websiteService.getWebsites().subscribe({
      next: websites => {
        console.log(websites,'websites');
        
        this.websites = websites;
        this.isLoading = false;
      },
      error: () => {
        this.errorMessage = 'خطا در دریافت وب‌سایت‌ها.';
        this.isLoading = false;
        console.log(Error , 'error');
        
      }
    });
  }

  private processCrawl(
    name: string,
    url: string,
    description: string
  ) {
    this.isCrawling = true;
    this.errorMessage = '';
    this.successMessage = '';

    this.websiteService.crawlWebsite(name, url, description).subscribe({
      next: response => {
        this.isCrawling = false;
        this.successMessage =
          `وب‌سایت با موفقیت پردازش شد. ${response.crawl.pages_processed} صفحه پردازش شد.`;

        this.websiteForm.reset();
        this.loadWebsites();
      },
      error: error => {
        this.isCrawling = false;
        this.errorMessage =
          error.error?.error || 'خطا در پردازش وب‌سایت.';
      }
    });
  }

  truncateUrl(url: string): string {
    const maxLength = 30;
    if (!url) return '';
    return url.length > maxLength ? url.substring(0, maxLength) + '...' : url;
  }

  selectedWebsiteIds = new Set<number>();

  toggleWebsite(id: number) {
    this.selectedWebsiteIds.has(id)
      ? this.selectedWebsiteIds.delete(id)
      : this.selectedWebsiteIds.add(id);
  }

  isSelected(id: number) {
    return this.selectedWebsiteIds.has(id);
  }

  startChat() {
    const websiteIds = [...this.selectedWebsiteIds];
    console.log(websiteIds , 'website ids');
    
    if (!websiteIds.length) return;

    this.chatService.createChat(
      'گفتگو با وب‌سایت‌ها',
      websiteIds
    ).subscribe({
      next: chat => {
        console.log('success');
        
        this.selectedWebsiteIds.clear();
        this.router.navigate(['/chats', chat.id]);
      },
      error: error => {
        this.errorMessage =
          error.error?.detail ||
          error.error?.error ||
          'خطا در ایجاد گفتگو.';
      }
    });
  }
}