import {
  afterNextRender,
  Component,
  effect,
  ElementRef,
  OnInit,
  signal,
  viewChild,
  WritableSignal,
} from '@angular/core';
import { ChatGraph, ChatService, ChatSession } from '../../services/chat';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import cytoscape from 'cytoscape';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-chat',
  imports: [FormsModule, CommonModule],
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
  showGraph = signal(false);
  graph = signal<ChatGraph | null>(null);
  chatId!: number;
  graphContainer = viewChild<ElementRef<HTMLDivElement>>('graphContainer');
  private cy: cytoscape.Core | null = null;
  isGraphLoading = signal(false);

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private chatService: ChatService,
  ) {
    effect(() => {
      const visible = this.showGraph();
      const graph = this.graph();
      const container = this.graphContainer();

      if (visible && graph && container) {
        this.renderGraph();
      }
    });
  }

  ngOnInit() {
    this.loadChats();

    this.route.paramMap.subscribe((params) => {
      this.chatId = Number(params.get('id'));

      this.graph.set(null);

      if (this.showGraph()) {
        this.loadGraph();
      }
      this.getChat(this.chatId);
    });
  }

  private getChat(id: number) {
    this.isLoading.set(true);
    this.chat.set(undefined);
    this.messages.set([]);

    this.chatService.getChat(id).subscribe({
      next: (chat) => {
        this.chat.set(chat);
        this.messages.set(chat.messages);
        this.isLoading.set(false);
      },
      error: () => this.isLoading.set(false),
    });
  }

  loadChats() {
    this.chatService.getChats().subscribe({ next: (chats) => this.chats.set(chats) });
  }

  newChat() {
    this.router.navigate(['/dashboard/chats']);
  }

  sendMessage() {
    const question = this.message().trim();
    const currentChat = this.chat();

    if (!question || !currentChat || this.isSending()) return;

    this.messages.update((messages) => [
      ...messages,
      { id: 0, role: 'user', content: question, created_at: '' },
    ]);

    this.message.set('');
    this.isSending.set(true);

    this.chatService.ask(currentChat.id, question).subscribe({
      next: (response) => {
        this.messages.update((messages) => [
          ...messages,
          {
            id: 0,
            role: 'assistant',
            content: response.answer,
            created_at: '',
          },
        ]);

        this.isSending.set(false);
        this.loadChats();
      },
      error: (error) => {
        this.messages.update((messages) => [
          ...messages,
          {
            id: 0,
            role: 'assistant',
            content: error.error?.error || 'خطا در دریافت پاسخ.',
            created_at: '',
          },
        ]);

        this.isSending.set(false);
      },
    });
  }

  loadGraph(): void {
    this.isGraphLoading.set(true);

    this.chatService.getGraph(this.chatId).subscribe({
      next: graph => {
        this.graph.set(graph);
        this.isGraphLoading.set(false);
      },
      error: () => {
        this.isGraphLoading.set(false);
      }
    });
  }

  toggleGraph(): void {
    this.showGraph.update(value => !value);

    if (this.showGraph() && !this.graph()) {
      this.loadGraph();
    }
  }

  private renderGraph(): void {

    if (this.cy) {
      this.cy.destroy();
      this.cy = null;
    }

    const container = this.graphContainer()?.nativeElement;
    const graph = this.graph();

    if (!container || !graph) {
      return;
    }

    const nodes = graph.nodes.slice(0, 20);
    const nodeIds = new Set(nodes.map((node) => node.id));

    const edges = Array.from(
      new Map(
        graph.edges
          .filter((edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target))
          .map((edge) => {
            const key = [edge.source, edge.target].sort().join('|');

            return [
              key,
              {
                data: {
                  id: key,
                  source: edge.source,
                  target: edge.target,
                },
              },
            ];
          }),
      ).values(),
    );

    cytoscape({
      container,
      elements: [
        ...nodes.map((node) => ({
          data: {
            id: node.id,
            label: node.label,
          },
        })),
        ...edges,
      ],
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#0d6efd',
            label: 'data(label)',
            color: '#ffffff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            'font-weight': 'bold',
            'text-wrap': 'wrap',
            'text-max-width': '100px',
            width: '70px',
            height: '70px',
            'border-width': 3,
            'border-color': '#ffffff',
          },
        },
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#adb5bd',
            'target-arrow-color': '#adb5bd',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
          },
        },
      ],
      layout: {
        name: 'cose',
        animate: true,
        padding: 40,
      },
    });
    container.style.backgroundColor = '#1e293b';
  }
}
