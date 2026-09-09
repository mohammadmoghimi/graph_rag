import { Component, computed, signal } from '@angular/core';
import { DashboardData, DashboardService } from '../../services/dashboard.service';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-dashboard-statistics',
  imports: [DatePipe],
  templateUrl: './dashboard-statistics.html',
  styleUrl: './dashboard-statistics.scss',
})
export class DashboardStatistics {
  dashboard = signal<DashboardData | null>(null);
  loading = signal(true);
  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.dashboardService.getDashboard().subscribe({
      next: (data) => {
        (this.dashboard.set(data), console.log(data, 'data'));
        this.loading.set(false);
      },
      error: (err) => {
        (console.error(err), this.loading.set(false));
      },
    });
  }

  timeAgo(dateString: string | null): string {
    if (!dateString) {
      return 'نامشخص';
    }

    const now = Date.now();
    const past = new Date(dateString).getTime();
    const diff = now - past; // milliseconds

    // Handle future dates (optional)
    if (diff < 0) {
      return 'در آینده';
    }

    const seconds = Math.floor(diff / 1000);

    if (seconds < 60) {
      return 'چند لحظه پیش';
    }

    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) {
      return `${this.toPersianDigits(minutes)} دقیقه پیش`;
    }

    const hours = Math.floor(minutes / 60);
    if (hours < 24) {
      return `${this.toPersianDigits(hours)} ساعت پیش`;
    }

    const days = Math.floor(hours / 24);
    if (days < 7) {
      return `${this.toPersianDigits(days)} روز پیش`;
    }

    const weeks = Math.floor(days / 7);
    if (weeks < 4) {
      return `${this.toPersianDigits(weeks)} هفته پیش`;
    }

    const months = Math.floor(days / 30); // approximate
    if (months < 12) {
      return `${this.toPersianDigits(months)} ماه پیش`;
    }

    const years = Math.floor(days / 365);
    return `${this.toPersianDigits(years)} سال پیش`;
  }

  toPersianDigits(num: number): string {
    const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
    return num
      .toString()
      .split('')
      .map((digit) => persianDigits[parseInt(digit, 10)])
      .join('');
  }

  totalPages = computed(() => {
    const data = this.dashboard();
    if (!data) {
      return 0;
    }
    return data.website_statistics.reduce((total, website) => total + website.pages, 0);
  });
  
  crawlSuccessRate = computed(() => {
    const data = this.dashboard();
    if (!data || data.statistics.crawls === 0) {
      return 0;
    }
    return Math.round((data.statistics.completed_crawls / data.statistics.crawls) * 100);
  });


latestWebsite = computed(() => {
  const websites = this.dashboard()?.website_statistics ?? [];

  return websites
    .filter(website => website.last_crawled_at)
    .sort(
      (a, b) =>
        new Date(b.last_crawled_at!).getTime() -
        new Date(a.last_crawled_at!).getTime()
    )[0] ?? null;
});

}
