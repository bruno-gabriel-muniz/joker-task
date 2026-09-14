/* eslint-disable @typescript-eslint/no-explicit-any */
import { inject, Injectable, Injector } from '@angular/core'
import { HttpStrategy, HttpStrategyConstructor } from './http-strategy'
import { Observable } from 'rxjs/internal/Observable'
import { catchError, throwError } from 'rxjs'
import { HttpErrorResponse } from '@angular/common/http'
import { Router } from '@angular/router'
import { environment } from '../../../environments/environment.development'

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  readonly baseUrl = environment.baseUrl
  private readonly router = inject(Router)
  private readonly injector = inject(Injector)

  private formatUrl(sufixUrl: string): string {
    return this.baseUrl + sufixUrl
  }

  execute<T extends HttpStrategy>(
    ClasseDoMetodo: HttpStrategyConstructor<T>,
    url: string,
    dados: any = null
  ): Observable<any> {
    const http = this.injector.get(ClasseDoMetodo)

    const result = http.execute(this.formatUrl(url), dados)

    return result.pipe(
      catchError((erro: HttpErrorResponse) => {
        console.error('Erro interceptado no pipe:', erro.message)

        if (erro.status === 401) {
          this.router.navigate(['/login'])
        }

        return throwError(() => new Error('Falha ao carregar os dados.'))
      })
    )
  }
}
