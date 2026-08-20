import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Website } from '../../services/website';
import { RouterOutlet } from "@angular/router";

@Component({
  selector: 'app-websites',
  imports: [CommonModule, FormsModule, RouterOutlet],
  templateUrl: './websites.html',
  styleUrl: './websites.scss',
})
export class Websites implements OnInit {
  websites: Website[] = [];

  name = '';
  url = '';
  description = '';

  errorMessage = '';
  successMessage = '';
  loading = false;

  constructor(
    private websiteService: Website
  ) {}

  ngOnInit() {
    this.loadWebsites();
  }

  loadWebsites() {
    this.websiteService.getWebsites().subscribe({
      next: websites => {
        this.websites = websites;
      },
      error: () => {
        this.errorMessage = 'Could not load websites.';
      }
    });
  }

  addWebsite() {
    this.errorMessage = '';
    this.successMessage = '';

    this.loading = true;

    this.websiteService.createWebsite(
      this.name,
      this.url,
      this.description
    ).subscribe({
      next: website => {
        this.websites.push(website);

        this.name = '';
        this.url = '';
        this.description = '';

        this.successMessage = 'Website added successfully.';
        this.loading = false;
      },
      error: () => {
        this.errorMessage = 'Could not add website.';
        this.loading = false;
      }
    });
  }

  deleteWebsite(id: number) {
    this.websiteService.deleteWebsite(id).subscribe({
      next: () => {
        this.websites = this.websites.filter(
          website => website.id !== id
        );
      },
      error: () => {
        this.errorMessage = 'Could not delete website.';
      }
    });
  }

  crawlWebsite(id: number) {
  this.websiteService.crawlWebsite(id).subscribe({
    next: () => {
      const website = this.websites.find(
        website => website.id === id
      );

      if (website) {
        website.status = 'pending';
      }
    },
    error: () => {
      this.errorMessage = 'Could not start crawl.';
    }
  });
}
}
