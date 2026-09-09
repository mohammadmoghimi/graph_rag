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
}
