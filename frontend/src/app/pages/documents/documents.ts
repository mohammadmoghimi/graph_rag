import { Component, signal } from '@angular/core';
import { DocumentItem, DocumentsService } from '../../services/documents.service';
import { DatePipe } from '@angular/common';

@Component({
  selector: 'app-documents',
  imports: [DatePipe],
  templateUrl: './documents.html',
  styleUrl: './documents.scss',
})
export class Documents {
  documents = signal<DocumentItem[]>([]);
  loading = signal(true);
  uploading = signal(false);

  selectedFile = signal<File | null>(null);
  name = signal('');
  description = signal('');

  constructor(private documentsService: DocumentsService) {}

  ngOnInit(): void {
    this.loadDocuments();
  }

  loadDocuments(): void {
    this.loading.set(true);

    this.documentsService.getDocuments().subscribe({
      next: documents => {
        this.documents.set(documents);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      }
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;

    this.selectedFile.set(file);

    if (file && !this.name()) {
      this.name.set(file.name);
    }
  }

  upload(): void {
    const file = this.selectedFile();

    if (!file || !this.name()) {
      return;
    }

    this.uploading.set(true);

    this.documentsService
      .uploadDocument(this.name(), this.description(), file)
      .subscribe({
        next: document => {
          this.documents.update(documents => [document, ...documents]);
          this.resetForm();
          this.uploading.set(false);
        },
        error: (err) => {
          this.uploading.set(false);
          console.log(err , 'error');
          
        }
      });
  }

  deleteDocument(document: DocumentItem): void {
    this.documentsService.deleteDocument(document.id).subscribe({
      next: () => {
        this.documents.update(
          documents => documents.filter(item => item.id !== document.id)
        );
      }
    });
  }

  resetForm(): void {
    this.selectedFile.set(null);
    this.name.set('');
    this.description.set('');
  }
}
