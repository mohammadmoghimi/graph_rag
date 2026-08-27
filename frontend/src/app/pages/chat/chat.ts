import { Component, OnInit, signal, WritableSignal } from '@angular/core';
import { ChatService, ChatSession } from '../../services/chat';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-chat',
  imports: [FormsModule],
  templateUrl: './chat.html',
  styleUrl: './chat.scss',
})
export class Chat implements OnInit {
  chat = signal<ChatSession | undefined>(undefined);
  chats = signal<ChatSession[]>([]);
  message = signal('');
  isLoading = signal(true);
  messages = signal<ChatSession['messages']>([]);
  isSending = signal(false);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private chatService: ChatService
  ) {}

  ngOnInit() {
    this.loadChats();

    this.route.paramMap.subscribe(params => {
      const id = Number(params.get('id'));
      this.getChat(id);
    });
  }

  private getChat(id: number) {
    this.isLoading.set(true);
    this.chat.set(undefined);
    this.messages.set([]);

    this.chatService.getChat(id).subscribe({
      next: chat => {
        this.chat.set(chat);
        this.messages.set(chat.messages);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false)
    });
  }

  loadChats() {
    this.chatService.getChats().subscribe({next: chats => this.chats.set(chats)});    
  }

  newChat() {
    this.router.navigate(['/dashboard/chats']);
  }

  sendMessage() {
    const question = this.message().trim();
    const currentChat = this.chat();

    if (!question || !currentChat || this.isSending()) return;

    this.messages.update(messages => [
      ...messages,
      { id: 0, role: 'user', content: question, created_at: '' }
    ]);

    this.message.set('');
    this.isSending.set(true);

    this.chatService.ask(currentChat.id, question).subscribe({
      next: response => {
        this.messages.update(messages => [
          ...messages,
          {
            id: 0,
            role: 'assistant',
            content: response.answer,
            created_at: ''
          }
        ]);

        this.isSending.set(false);
        this.loadChats();
      },
      error: error => {
        this.messages.update(messages => [
          ...messages,
          {
            id: 0,
            role: 'assistant',
            content: error.error?.error || 'خطا در دریافت پاسخ.',
            created_at: ''
          }
        ]);

        this.isSending.set(false);
      }
    });
  }
}