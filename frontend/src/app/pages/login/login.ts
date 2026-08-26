import { Component, OnInit, signal, WritableSignal } from '@angular/core';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { Auth } from '../../services/auth';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-login',
  imports: [ReactiveFormsModule, CommonModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login implements OnInit {
  isSignup = signal(false);
  isLoading = signal(false);
  errorMessage = signal('');

  loginForm!: FormGroup;
  signupForm!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private auth: Auth,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loginForm = this.fb.nonNullable.group({
      username: ['', Validators.required],
      password: ['', Validators.required]
    });

    this.signupForm = this.fb.nonNullable.group({
      username: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      password: ['', [Validators.required, Validators.minLength(8)]]
    });
  }

  switchMode(signup: boolean) {
    this.isSignup.set(signup);
    this.errorMessage.set('');
  }

  login() {
    if (this.loginForm.invalid || this.isLoading()) return;

    this.isLoading.set(true);
    this.errorMessage.set('');

    const { username, password } = this.loginForm.getRawValue();

    this.auth.login(username, password).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: error => {
        this.isLoading.set(false);
        this.errorMessage.set(
          'نام کاربری یا رمز عبور اشتباه است.'
        );
      }
    });
  }

  signup() {
    if (this.signupForm.invalid || this.isLoading()) return;

    this.isLoading.set(true);
    this.errorMessage.set('');

    this.auth.signup(this.signupForm.getRawValue()).subscribe({
      next: () => {
        const { username, password } = this.signupForm.getRawValue();

        this.auth.login(username, password).subscribe({
          next: () => this.router.navigate(['/dashboard']),
          error: () => {
            this.isLoading.set(false);
            this.errorMessage.set('ثبت‌نام انجام شد. ورود ناموفق بود.');
          }
        });
      },
      error: error => {
        this.isLoading.set(false);
        this.errorMessage.set(
          error.error?.username?.[0] ||
          error.error?.email?.[0] ||
          error.error?.detail ||
          'ثبت‌نام انجام نشد.'
        );
      }
    });
  }
}