import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DashboardStatistics {
  websites: number;
  crawls: number;
  completed_crawls: number;
  failed_crawls: number;
  chunks: number;
  entities: number;
  documents: number;
  completed_documents: number;
  failed_documents: number;
  processing_documents: number;
  document_chunks: number;
  document_entities: number;
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
  crawls_per_day: CrawlDay[];
  website_statistics: WebsiteStatistics[];
  document_statistics: DocumentStatistics[];
  recent_activity: Activity[];
  system_status: SystemStatus;
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

export interface DocumentStatistics {
  id: number;
  name: string;
  chunks: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CrawlDay {
  date: string;
  count: number;
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