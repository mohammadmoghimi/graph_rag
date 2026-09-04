import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Website {
  id: number;
  name: string;
  url: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
  last_crawled_at: string | null;
}

export interface Crawl {
  id: number;
  website: number;
  status: string;
  pages_found: number;
  pages_processed: number;
  error_message: string;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface CrawlResponse {
  website: Website;
  crawl: Crawl;
}

@Injectable({
  providedIn: 'root',
})
export class WebsiteService {
    private apiUrl = 'http://127.0.0.1:8000/api/websites';

  constructor(private http: HttpClient) {}

  getWebsites(): Observable<Website[]> {
    return this.http.get<Website[]>(`${this.apiUrl}/`);
  }

  createWebsite(
    name: string,
    url: string,
    description: string
  ): Observable<Website> {

    return this.http.post<Website>(
      `${this.apiUrl}/`,
      {
        name,
        url,
        description
      }
    );
  }

  updateWebsite(id: number, data: { name: string; description: string }): Observable<Website> {
    return this.http.patch<Website>(`${this.apiUrl}/${id}/`, data);
  }

  deleteWebsite(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}/`);
  }

  crawlWebsite(name: string , url:string , description:string):Observable<CrawlResponse> {
    return this.http.post<CrawlResponse>(`${this.apiUrl}/crawl/`,{name, url , description});
  }
  
}
