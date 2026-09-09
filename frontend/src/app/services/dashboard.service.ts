import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DashboardStatistics {
  websites: number;
  crawls: number;
  chunks: number;
  entities: number;
}

export interface Activity {
  type: string;
  message: string;
  created_at: string;
}

export interface SystemStatus {
  api: string;
  elasticsearch: string;
  neo4j: string;
}

export interface DashboardData {
  statistics: DashboardStatistics;
  recent_activity: Activity[];
  system_status: SystemStatus;
  website_statistics: WebsiteStatistics[];
}

export interface WebsiteStatistics {
  id: number;
  name: string;
  crawls: number;
  pages: number;
  chunks: number;
  entities: number;
  last_crawled_at: string | null;
  status: string;
}

@Injectable({
  providedIn: 'root'
})
export class DashboardService {
  private apiUrl = 'http://127.0.0.1:8000/api/dashboard/';

  constructor(private http: HttpClient) {}

  getDashboard(): Observable<DashboardData> {
    return this.http.get<DashboardData>(this.apiUrl);
  }
}