import { Component, OnInit, signal, WritableSignal } from '@angular/core';
import { ChatService, ChatSession } from '../../services/chat';
import { ActivatedRoute } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chat',
  imports: [FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.scss',
})
export class Chat implements OnInit {
  // State converted to signals
  chat = signal<ChatSession | undefined>(undefined);
  message = signal('');
  isLoading = signal(true);
  messages = signal<{ role: string; content: string }[]>([]);
  isSending = signal(false);

  constructor(
    private route: ActivatedRoute,
    private chatService: ChatService
  ) {}

  ngOnInit() {
    const id = Number(this.route.snapshot.paramMap.get('id'));

    this.chatService.getChat(id).subscribe({
      next: chat => {
        this.chat.set(chat);
        this.isLoading.set(false);
      },
      error: () => {
        this.isLoading.set(false);
      }
    });
  }

  sendMessage() {
    const question = this.message().trim();
    const currentChat = this.chat();

    if (!question || !currentChat || this.isSending()) {
      return;
    }

    // Add user message to the list
    this.messages.update(prev => [
      ...prev,
      { role: 'user', content: question }
    ]);

    // Clear the input field
    this.message.set('');
    this.isSending.set(true);

    this.chatService.ask(currentChat.id, question).subscribe({
      next: response => {
        this.messages.update(prev => [
          ...prev,
          { role: 'assistant', content: response.answer }
        ]);
        this.isSending.set(false);
      },
      error: error => {
        this.messages.update(prev => [
          ...prev,
          { role: 'assistant', content: error.error?.error || 'خطا در دریافت پاسخ.' }
        ]);
        this.isSending.set(false);
      }
    });
  }
}