import { ChatService } from './../../services/chat';
import { Component, signal } from '@angular/core';
import { DocumentItem, DocumentsService } from '../../services/documents.service';
import { DatePipe } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { Modal } from '../modal/modal';

@Component({
  selector: 'app-documents',
  imports: [FormsModule , Modal],
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
  selectedDocumentIds = signal<Set<number>>(new Set());
  editingDocument = signal<DocumentItem | null>(null);
  editName = '';
  editDescription = '';

  constructor(
    private documentsService: DocumentsService,
    private chatService: ChatService,
    private router: Router,
  ) {}

  ngOnInit(): void {
    this.loadDocuments();
  }

  loadDocuments(): void {
    this.loading.set(true);

    this.documentsService.getDocuments().subscribe({
      next: (documents) => {
        this.documents.set(documents);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
      },
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

    this.documentsService.uploadDocument(this.name(), this.description(), file).subscribe({
      next: (document) => {
        this.documents.update((documents) => [document, ...documents]);
        this.resetForm();
        this.uploading.set(false);
      },
      error: (err) => {
        this.uploading.set(false);
        console.log(err, 'error');
      },
    });
  }

  deleteDocument(id: number) {
    if (!confirm('آیا از حذف این سند مطمئن هستید؟')) return;

    this.documentsService.deleteDocument(id).subscribe({
      next: (res) => {
        console.log(res);

        this.documents.update(documents =>
          documents.filter(w => w.id !== id)
        );
      }
    });
  }

  resetForm(): void {
    this.selectedFile.set(null);
    this.name.set('');
    this.description.set('');
  }

  toggleDocument(id: number) {
    this.selectedDocumentIds.update((set) => {
      const newSet = new Set(set);
      newSet.has(id) ? newSet.delete(id) : newSet.add(id);
      return newSet;
    });
  }

  isSelected(id: number) {
    return this.selectedDocumentIds().has(id);
  }

  startChat() {
    const documentIds = [...this.selectedDocumentIds()];

    if (!documentIds.length) return;

    const selectedDocuments = this.documents().filter((document) =>
      documentIds.includes(document.id),
    );

    const title =
      selectedDocuments.length <= 2
        ? selectedDocuments.map((document) => document.name).join(' و ')
        : `${selectedDocuments[0].name}، ${selectedDocuments[1].name} و ${selectedDocuments.length - 2} سند دیگر`;

    this.chatService.createChat(title, [], documentIds).subscribe({
      next: (chat) => {
        this.selectedDocumentIds.set(new Set());
        this.router.navigate(['/chats', chat.id]);
      },
      error: (error) => {
        console.log(error, 'error');
      },
    });
  }

  editDocument(document: DocumentItem): void {
    this.editingDocument.set(document);
    this.editName = document.name;
    this.editDescription = document.description;
  }

  cancelEdit(): void {
    this.editingDocument.set(null);
    this.editName = '';
    this.editDescription = '';
  }

  saveDocument(): void {
    const document = this.editingDocument();

    if (!document || !this.editName.trim()) return;

    this.documentsService
      .updateDocument(document.id, this.editName.trim(), this.editDescription.trim())
      .subscribe({
        next: (updatedDocument) => {
          this.documents.update((documents) =>
            documents.map((d) => (d.id === updatedDocument.id ? updatedDocument : d)),
          );

          this.cancelEdit();
        },
        error: (error) => {
          console.log(error , 'error');
          ;
        },
      });
  }
}
