import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DocumentItem {
  id: number;
  name: string;
  description: string;
  status: string;
  created_at: string;
  updated_at: string;
}

@Injectable({
  providedIn: 'root'
})
export class DocumentsService {
  private readonly url = 'http://127.0.0.1:8000/api/documents';

  constructor(private http: HttpClient) {}

  getDocuments(): Observable<DocumentItem[]> {
    return this.http.get<DocumentItem[]>(this.url);
  }

  uploadDocument(
    name: string,
    description: string,
    file: File
  ): Observable<DocumentItem> {
    const formData = new FormData();

    formData.append('name', name);
    formData.append('description', description);
    formData.append('file', file);

    return this.http.post<DocumentItem>(
      `${this.url}/upload/`,
      formData
    );
  }

  deleteDocument(id: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}/`);
  }
}