import { Component, signal } from '@angular/core';
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

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.dashboardService.getDashboard().subscribe({
      next: data => {this.dashboard.set(data) ,console.log(data , 'data') ;
      },
      error: err => console.error(err),
      complete: () => console.log(this.dashboard)
    });
  }


timeAgo(dateString: string): string {
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


}
