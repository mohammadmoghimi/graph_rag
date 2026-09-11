import {
  AfterViewInit,
  Directive,
  ElementRef,
  HostListener,
  Input,
  OnChanges,
  OnDestroy,
  SimpleChanges,
  inject,
} from '@angular/core';

type RevealVariant = 'up' | 'down' | 'left' | 'right' | 'scale' | 'zoom' | 'flip';

/**
 * Adds a scroll-triggered entrance animation. Place on a wrapper element
 * and combine with `revealDelay` for staggered grids.
 */
@Directive({
  selector: '[appReveal]',
  standalone: true,
})
export class RevealDirective implements AfterViewInit, OnDestroy {
  private el = inject<ElementRef<HTMLElement>>(ElementRef);
  private observer?: IntersectionObserver;

  @Input() appReveal: RevealVariant = 'up';
  @Input() revealDelay = 0;
  @Input() revealThreshold = 0.12;

  ngAfterViewInit(): void {
    const node = this.el.nativeElement;
    node.classList.add('reveal', `reveal-${this.appReveal}`);
    if (this.revealDelay) node.style.transitionDelay = `${this.revealDelay}ms`;

    if (typeof IntersectionObserver === 'undefined') {
      node.classList.add('reveal-visible');
      return;
    }

    this.observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            node.classList.add('reveal-visible');
            this.observer?.unobserve(node);
            break;
          }
        }
      },
      { threshold: this.revealThreshold, rootMargin: '0px 0px -60px 0px' },
    );

    this.observer.observe(node);
  }

  ngOnDestroy(): void {
    this.observer?.disconnect();
  }
}

/**
 * Animates a number from 0 → target once it scrolls into view.
 * The host element's text content is overwritten.
 */
@Directive({
  selector: '[appCountUp]',
  standalone: true,
})
export class CountUpDirective implements AfterViewInit, OnChanges, OnDestroy {
  private el = inject<ElementRef<HTMLElement>>(ElementRef);
  private observer?: IntersectionObserver;
  private rafId: number | null = null;
  private hasEntered = false;

  @Input('appCountUp') target: number | string | null = 0;
  @Input() countDuration = 1600;
  @Input() countSuffix = '';

  ngAfterViewInit(): void {
    this.el.nativeElement.textContent = `0${this.countSuffix}`;

    if (typeof IntersectionObserver === 'undefined') {
      this.hasEntered = true;
      this.animate();
      return;
    }

    this.observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            this.hasEntered = true;
            this.animate();
            this.observer?.disconnect();
            break;
          }
        }
      },
      { threshold: 0.35 },
    );

    this.observer.observe(this.el.nativeElement);
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (this.hasEntered && changes['target']) {
      this.animate();
    }
  }

  private animate(): void {
    if (this.rafId !== null) cancelAnimationFrame(this.rafId);

    const target = Number(this.target) || 0;
    const duration = Math.max(200, this.countDuration);
    const start = performance.now();

    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = t === 1 ? 1 : 1 - Math.pow(2, -10 * t); // easeOutExpo
      const value = Math.round(target * eased);
      this.el.nativeElement.textContent = `${value.toLocaleString('en-US')}${this.countSuffix}`;

      if (t < 1) {
        this.rafId = requestAnimationFrame(tick);
      } else {
        this.rafId = null;
      }
    };

    this.rafId = requestAnimationFrame(tick);
  }

  ngOnDestroy(): void {
    this.observer?.disconnect();
    if (this.rafId !== null) cancelAnimationFrame(this.rafId);
  }
}

/**
 * Subtle 3D tilt + cursor spotlight. Publishes CSS vars:
 *   --tilt-x, --tilt-y, --tilt-scale, --mx, --my
 */
@Directive({
  selector: '[appTilt]',
  standalone: true,
})
export class TiltDirective {
  private el = inject<ElementRef<HTMLElement>>(ElementRef);

  @Input() tiltMax = 8;
  @Input() tiltScale = 1.015;

  @HostListener('mousemove', ['$event'])
  onMove(event: MouseEvent): void {
    const node = this.el.nativeElement;
    const rect = node.getBoundingClientRect();
    if (!rect.width || !rect.height) return;

    const px = (event.clientX - rect.left) / rect.width;
    const py = (event.clientY - rect.top) / rect.height;

    const rx = (0.5 - py) * this.tiltMax * 2;
    const ry = (px - 0.5) * this.tiltMax * 2;

    node.style.setProperty('--tilt-x', `${rx.toFixed(2)}deg`);
    node.style.setProperty('--tilt-y', `${ry.toFixed(2)}deg`);
    node.style.setProperty('--tilt-scale', `${this.tiltScale}`);
    node.style.setProperty('--mx', `${(px * 100).toFixed(2)}%`);
    node.style.setProperty('--my', `${(py * 100).toFixed(2)}%`);
  }

  @HostListener('mouseleave')
  onLeave(): void {
    const node = this.el.nativeElement;
    node.style.setProperty('--tilt-x', '0deg');
    node.style.setProperty('--tilt-y', '0deg');
    node.style.setProperty('--tilt-scale', '1');
  }
}