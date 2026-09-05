import { ChatService } from './../../services/chat';
import { Component, OnInit, signal, WritableSignal } from '@angular/core';
import {
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators
} from '@angular/forms';
import { Website, WebsiteService } from '../../services/website';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-websites',
  standalone: true,
  imports: [ReactiveFormsModule, FormsModule],
  templateUrl: './websites.html',
  styleUrl: './websites.scss'
})
export class Websites implements OnInit {

  websiteForm!: FormGroup;
  websites = signal<Website[]>([]);
  isCrawling = signal(false);
  isLoading = signal(true);
  errorMessage = signal('');
  successMessage = signal('');
  selectedWebsiteIds = signal<Set<number>>(new Set());
  editingWebsite = signal<Website | null>(null);
  editName = '';
  editDescription = '';
  openMenu = signal<number | null>(null);

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
    if (this.websiteForm.invalid || this.isCrawling()) {
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
        
        this.websites.set(websites);
        this.isLoading.set(false);
      },
      error: () => {
        this.errorMessage.set('خطا در دریافت وب‌سایت‌ها.');
        this.isLoading.set(false);
        console.log(Error , 'error');
        
      }
    });
  }

  private processCrawl(
    name: string,
    url: string,
    description: string
  ) {
  this.isCrawling.set(true);
  this.errorMessage.set('');
  this.successMessage.set('');

    this.websiteService.crawlWebsite(name, url, description).subscribe({
      next: response => {
        this.isCrawling.set(false);
        this.successMessage.set(
          `وب‌سایت با موفقیت پردازش شد. ${response.crawl.pages_processed} صفحه پردازش شد.`
        );

        this.websiteForm.reset();
        this.loadWebsites();
      },
      error: error => {
        this.isCrawling.set(false);
        this.errorMessage.set(
          error.error?.error || 'خطا در پردازش وب‌سایت.'
        );
      }
    });
  }

  editWebsite(website: Website) {
  this.editingWebsite.set(website);
  this.editName = website.name;
  this.editDescription = website.description || '';
}

  saveWebsite() {
    const website = this.editingWebsite();

    if (!website || !this.editName.trim()) return;

    this.websiteService.updateWebsite(website.id, {
      name: this.editName.trim(),
      description: this.editDescription.trim()
    }).subscribe({
      next: updated => {
        this.websites.update(websites =>
          websites.map(w => w.id === updated.id ? updated : w)
        );
        this.editingWebsite.set(null);
      }
    });
  }

  cancelEdit() {
    this.editingWebsite.set(null);
  }

  deleteWebsite(id: number) {
    if (!confirm('آیا از حذف این وب‌سایت مطمئن هستید؟')) return;

    this.websiteService.deleteWebsite(id).subscribe({
      next: (res) => {
        console.log(res);
        
        this.websites.update(websites =>
          websites.filter(w => w.id !== id)
        );
      }
    });
  }

  truncateUrl(url: string): string {
    const maxLength = 30;
    if (!url) return '';
    return url.length > maxLength ? url.substring(0, maxLength) + '...' : url;
  }

  toggleMenu(id: number) {
  this.openMenu.update(current => current === id ? null : id);
  }

  toggleWebsite(id: number) {
    this.selectedWebsiteIds.update(set => {
      const newSet = new Set(set);
      newSet.has(id) ? newSet.delete(id) : newSet.add(id);
      return newSet;
    });
  }

  isSelected(id: number) {
    return this.selectedWebsiteIds().has(id);
  }

  startChat() {
    const websiteIds = [...this.selectedWebsiteIds()];
    console.log(websiteIds , 'website ids');
    
    if (!websiteIds.length) return;

  const selectedWebsites = this.websites().filter(w =>
    websiteIds.includes(w.id)
  );

  const title = selectedWebsites.length <= 2
    ? selectedWebsites.map(w => w.name).join(' و ')
    : `${selectedWebsites[0].name}، ${selectedWebsites[1].name} و ${selectedWebsites.length - 2} وب‌سایت دیگر`;

    this.chatService.createChat(
      title,
      websiteIds
    ).subscribe({
      next: chat => {
        console.log('success');
        
        this.selectedWebsiteIds.set(new Set());
        this.router.navigate(['/chats', chat.id]);
      },
      error: error => {
        this.errorMessage.set(
          error.error?.detail ||
          error.error?.error ||
          'خطا در ایجاد گفتگو.'
        );
      }
    });
  }
}