import { HttpClient } from '@angular/common/http'
import { inject, Injectable } from '@angular/core'
import { Observable } from 'rxjs'

export interface HttpStrategy {
  execute(
    url: string,
    body: Record<string, string | string[]> | null
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ): Observable<any>
}

@Injectable({ providedIn: 'root' })
export class GetHttp implements HttpStrategy {
  private http = inject(HttpClient)

  execute(url: string, body: Record<string, string | string[]> | null) {
    return this.http.get(url, {
      params: body ?? undefined,
      withCredentials: true,
    })
  }
}

@Injectable({ providedIn: 'root' })
export class PostHttp implements HttpStrategy {
  private http = inject(HttpClient)

  execute(url: string, body: Record<string, string | string[]> | null) {
    return this.http.post(url, body, { withCredentials: true })
  }
}

@Injectable({ providedIn: 'root' })
export class PutHttp implements HttpStrategy {
  private http = inject(HttpClient)

  execute(url: string, body: Record<string, string | string[]> | null) {
    return this.http.put(url, body, { withCredentials: true })
  }
}

@Injectable({ providedIn: 'root' })
export class PatchHttp implements HttpStrategy {
  private http = inject(HttpClient)

  execute(url: string, body: Record<string, string | string[]> | null) {
    return this.http.patch(url, body, { withCredentials: true })
  }
}

@Injectable({ providedIn: 'root' })
export class DeleteHttp implements HttpStrategy {
  private http = inject(HttpClient)

  execute(url: string, body: Record<string, string | string[]> | null) {
    if (body !== null) console.log('Warning') // TODO
    return this.http.delete(url, { withCredentials: true })
  }
}

export type HttpStrategyConstructor<T extends HttpStrategy> = new (
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ...args: any[]
) => T
