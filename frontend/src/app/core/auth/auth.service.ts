import { inject, Injectable } from '@angular/core'
import { ApiService } from '../api/api.service'
import { PostHttp } from '../api/http-strategy'

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private api = inject(ApiService)

  login(email: string, password: string): void {
    this.api.execute(PostHttp, '/login', {
      username: email,
      password: password,
    })
  }

  logout() {
    this.api.execute(PostHttp, '/logout', {})
  }
}
