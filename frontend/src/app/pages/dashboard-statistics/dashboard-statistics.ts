import { Component, computed, signal } from '@angular/core';
import { DashboardData, DashboardService } from '../../services/dashboard.service';
import { DatePipe } from '@angular/common';
import { Chart, ChartOptions, registerables } from 'chart.js';
import {
  CountUpDirective,
  RevealDirective,
  TiltDirective,
} from './dashboard-animations';

Chart.register(...registerables);

@Component({
  selector: 'app-dashboard-statistics',
  imports: [RevealDirective, CountUpDirective, TiltDirective],
  templateUrl: './dashboard-statistics.html',
  styleUrl: './dashboard-statistics.scss',
})
export class DashboardStatistics {
  dashboard = signal<DashboardData | null>(null);
  loading = signal(true);

  crawlChart = signal<Chart | null>(null);
  chunkChart = signal<Chart | null>(null);
  entityChart = signal<Chart | null>(null);
  crawlStatusChart = signal<Chart | null>(null);
  documentChunkChart = signal<Chart | null>(null);
  documentStatusChart = signal<Chart | null>(null);

  private readonly palette = {
    purple: '#8b5cf6',
    purpleFill: 'rgba(139, 92, 246, 1)',
    cyan: '#06b6d4',
    pink: '#ec4899',
    emerald: '#10b981',
    amber: '#f59e0b',
    rose: '#f43f5e',
    grid: 'rgba(148, 163, 184, .14)',
    tick: '#94a3b8',
  };

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.dashboardService.getDashboard().subscribe({
      next: (data) => {
        this.dashboard.set(data);
        this.loading.set(false);

        // Wait for the @if block to render before hooking charts to scroll.
        setTimeout(() => {
          this.observeForRender('crawlChart', () => this.renderCrawlChart());
          this.observeForRender('crawlStatusChart', () => this.renderCrawlStatusChart());
          this.observeForRender('chunksChart', () => this.renderChunksChart());
          this.observeForRender('entitiesChart', () => this.renderEntitiesChart());
          this.observeForRender('documentStatusChart', () => this.renderDocumentStatusChart());
          this.observeForRender('documentChunksChart', () => this.renderDocumentChunksChart());
        }, 0);
      },
      error: (err) => {
        console.error(err);
        this.loading.set(false);
      },
    });
  }

  // ── Stat cards driving the hero grid (enables stagger + accent rotation) ──
  statCards = computed(() => {
    const data = this.dashboard();
    if (!data) return [];

    return [
      { icon: 'bi-globe2', label: 'وب‌سایت‌ها', value: data.statistics.websites, suffix: '' },
      { icon: 'bi-file-earmark-text', label: 'اسناد', value: data.statistics.documents, suffix: '' },
      { icon: 'bi-boxes', label: 'چانک‌های وب‌سایت', value: data.statistics.chunks, suffix: '' },
      { icon: 'bi-files', label: 'چانک‌های اسناد', value: data.statistics.document_chunks, suffix: '' },
      { icon: 'bi-diagram-3', label: 'موجودیت‌های وب‌سایت', value: data.statistics.entities, suffix: '' },
      { icon: 'bi-diagram-2', label: 'موجودیت‌های اسناد', value: data.statistics.document_entities, suffix: '' },
      { icon: 'bi-file-text', label: 'صفحات', value: this.totalPages(), suffix: '' },
      { icon: 'bi-check-circle', label: 'موفقیت خزش', value: this.crawlSuccessRate(), suffix: '%' },
    ];
  });

  timeAgo(dateString: string | null): string {
    if (!dateString) return 'نامشخص';

    const now = Date.now();
    const past = new Date(dateString).getTime();
    const diff = now - past;

    if (diff < 0) return 'در آینده';

    const seconds = Math.floor(diff / 1000);
    if (seconds < 60) return 'چند لحظه پیش';

    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${this.toPersianDigits(minutes)} دقیقه پیش`;

    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${this.toPersianDigits(hours)} ساعت پیش`;

    const days = Math.floor(hours / 24);
    if (days < 7) return `${this.toPersianDigits(days)} روز پیش`;

    const weeks = Math.floor(days / 7);
    if (weeks < 4) return `${this.toPersianDigits(weeks)} هفته پیش`;

    const months = Math.floor(days / 30);
    if (months < 12) return `${this.toPersianDigits(months)} ماه پیش`;

    const years = Math.floor(days / 365);
    return `${this.toPersianDigits(years)} سال پیش`;
  }

  toPersianDigits(num: number): string {
    const persianDigits = '۰۱۲۳۴۵۶۷۸۹';
    return num
      .toString()
      .split('')
      .map((digit) => persianDigits[parseInt(digit, 10)])
      .join('');
  }

  totalPages = computed(() => {
    const data = this.dashboard();
    if (!data) return 0;
    return data.website_statistics.reduce((total, website) => total + website.pages, 0);
  });

  crawlSuccessRate = computed(() => {
    const data = this.dashboard();
    if (!data || data.statistics.crawls === 0) return 0;
    return Math.round((data.statistics.completed_crawls / data.statistics.crawls) * 100);
  });

  latestWebsite = computed(() => {
    const websites = this.dashboard()?.website_statistics ?? [];
    return (
      websites
        .filter((website) => website.last_crawled_at)
        .sort(
          (a, b) => new Date(b.last_crawled_at!).getTime() - new Date(a.last_crawled_at!).getTime(),
        )[0] ?? null
    );
  });

  latestDocument = computed(() => {
    const documents = this.dashboard()?.document_statistics ?? [];
    return (
      documents
        .filter((document) => document.status === 'completed')
        .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())[0] ??
      null
    );
  });

  // ── Lazy chart mounting — only renders once the canvas scrolls in ───────
  private observeForRender(id: string, cb: () => void, delay = 80): void {
    const el = document.getElementById(id);
    if (!el) return;

    if (typeof IntersectionObserver === 'undefined') {
      setTimeout(cb, 0);
      return;
    }

    const obs = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            obs.disconnect();
            setTimeout(cb, delay);
            break;
          }
        }
      },
      { threshold: 0.15, rootMargin: '0px 0px -50px 0px' },
    );
    obs.observe(el);
  }

  // ── Line chart ──────────────────────────────────────────────────────────
  renderCrawlChart(): void {
    const data = this.dashboard();
    if (!data) return;

    const canvas = document.getElementById('crawlChart') as HTMLCanvasElement | null;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const gradient = ctx.createLinearGradient(0, 0, 0, 320);
    gradient.addColorStop(0, 'rgba(139, 92, 246, 0.55)');
    gradient.addColorStop(0.55, 'rgba(139, 92, 246, 0.15)');
    gradient.addColorStop(1, 'rgba(139, 92, 246, 0)');

    const labels = data.crawls_per_day.map((item) =>
      new Date(item.date).toLocaleDateString('fa-IR', { weekday: 'short' }),
    );
    const values = data.crawls_per_day.map((item) => item.count);

    this.crawlChart()?.destroy();

    this.crawlChart.set(
      new Chart(canvas, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: 'خزش‌ها',
              data: values,
              borderColor: this.palette.purple,
              backgroundColor: gradient,
              borderWidth: 3,
              tension: 0.42,
              fill: true,
              pointBackgroundColor: '#fff',
              pointBorderColor: this.palette.purple,
              pointBorderWidth: 3,
              pointRadius: 0,
              pointHoverRadius: 7,
              pointHitRadius: 22,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: { duration: 1800, easing: 'easeOutExpo' },
          interaction: { intersect: false, mode: 'index' },
          plugins: { legend: { display: false } },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { precision: 0, color: this.palette.tick, font: { family: 'inherit' } },
              grid: { color: this.palette.grid, drawTicks: false },
              border: { display: false },
            },
            x: {
              ticks: { color: this.palette.tick, font: { family: 'inherit' } },
              grid: { display: false },
              border: { display: false },
            },
          },
        },
      }),
    );
  }

  // ── Website bar charts (split so each can reveal independently) ─────────
  private horizontalBarOptions(): ChartOptions<'bar'> {
    return {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 1400, easing: 'easeOutQuart' },
      plugins: { legend: { display: false } },
      scales: {
        x: {
          beginAtZero: true,
          ticks: { precision: 0, color: this.palette.tick, font: { family: 'inherit' } },
          grid: { color: this.palette.grid, drawTicks: false },
          border: { display: false },
        },
        y: {
          ticks: { color: this.palette.tick, font: { family: 'inherit' } },
          grid: { display: false },
          border: { display: false },
        },
      },
    };
  }

  renderChunksChart(): void {
    const data = this.dashboard();
    if (!data) return;

    const canvas = document.getElementById('chunksChart') as HTMLCanvasElement | null;
    if (!canvas) return;

    this.chunkChart()?.destroy();

    this.chunkChart.set(
      new Chart(canvas, {
        type: 'bar',
        data: {
          labels: data.website_statistics.map((w) => w.name),
          datasets: [
            {
              label: 'Chunks',
              data: data.website_statistics.map((w) => w.chunks),
              backgroundColor: this.palette.purple,
              hoverBackgroundColor: this.palette.pink,
              borderRadius: 8,
              barThickness: 16,
            },
          ],
        },
        options: this.horizontalBarOptions(),
      }),
    );
  }

  renderEntitiesChart(): void {
    const data = this.dashboard();
    if (!data) return;

    const canvas = document.getElementById('entitiesChart') as HTMLCanvasElement | null;
    if (!canvas) return;

    this.entityChart()?.destroy();

    this.entityChart.set(
      new Chart(canvas, {
        type: 'bar',
        data: {
          labels: data.website_statistics.map((w) => w.name),
          datasets: [
            {
              label: 'Entities',
              data: data.website_statistics.map((w) => w.entities),
              backgroundColor: this.palette.cyan,
              hoverBackgroundColor: this.palette.emerald,
              borderRadius: 8,
              barThickness: 16,
            },
          ],
        },
        options: this.horizontalBarOptions(),
      }),
    );
  }

  // ── Crawl status pie ────────────────────────────────────────────────────
  renderCrawlStatusChart(): void {
    const data = this.dashboard();
    if (!data) return;

    const canvas = document.getElementById('crawlStatusChart') as HTMLCanvasElement | null;
    if (!canvas) return;

    this.crawlStatusChart()?.destroy();

    const completed = data.statistics.completed_crawls;
    const failed = data.statistics.failed_crawls;
    const running = Math.max(0, data.statistics.crawls - completed - failed);

    this.crawlStatusChart.set(
      new Chart(canvas, {
        type: 'pie',
        data: {
          labels: ['تکمیل شده', 'ناموفق', 'در حال اجرا'],
          datasets: [
            {
              data: [completed, failed, running],
              backgroundColor: [this.palette.emerald, this.palette.rose, this.palette.amber],
              hoverOffset: 10,
              borderWidth: 0,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          animation: {
            animateRotate: true,
            animateScale: true,
            duration: 1500,
            easing: 'easeOutQuart',
          },
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 16,
                usePointStyle: true,
                pointStyle: 'circle',
                color: this.palette.tick,
                font: { family: 'inherit' },
              },
            },
          },
        },
      }),
    );
  }

  // ── Document charts ─────────────────────────────────────────────────────
  renderDocumentStatusChart(): void {
    const data = this.dashboard();
    if (!data) return;

    const canvas = document.getElementById('documentStatusChart') as HTMLCanvasElement | null;
    if (!canvas) return;

    this.documentStatusChart()?.destroy();

    const completed = data.statistics.completed_documents;
    const failed = data.statistics.failed_documents;
    const processing = data.statistics.processing_documents;

    this.documentStatusChart.set(
      new Chart(canvas, {
        type: 'doughnut',
        data: {
          labels: ['تکمیل شده', 'ناموفق', 'در حال پردازش'],
          datasets: [
            {
              data: [completed, failed, processing],
              backgroundColor: [this.palette.emerald, this.palette.rose, this.palette.amber],
              hoverOffset: 10,
              borderWidth: 0,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '62%',
          animation: {
            animateRotate: true,
            animateScale: true,
            duration: 1500,
            easing: 'easeOutQuart',
          },
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                padding: 16,
                usePointStyle: true,
                pointStyle: 'circle',
                color: this.palette.tick,
                font: { family: 'inherit' },
              },
            },
          },
        },
      }),
    );
  }

  renderDocumentChunksChart(): void {
    const data = this.dashboard();
    if (!data) return;

    const canvas = document.getElementById('documentChunksChart') as HTMLCanvasElement | null;
    if (!canvas) return;

    this.documentChunkChart()?.destroy();

    this.documentChunkChart.set(
      new Chart(canvas, {
        type: 'bar',
        data: {
          labels: data.document_statistics.map((d) => d.name),
          datasets: [
            {
              label: 'Chunks',
              data: data.document_statistics.map((d) => d.chunks),
              backgroundColor: this.palette.pink,
              hoverBackgroundColor: this.palette.purple,
              borderRadius: 8,
              barThickness: 16,
            },
          ],
        },
        options: this.horizontalBarOptions(),
      }),
    );
  }
}