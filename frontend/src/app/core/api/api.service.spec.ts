/* eslint-disable @typescript-eslint/no-explicit-any */
import { TestBed } from '@angular/core/testing'

import { ApiService } from './api.service'
import { throwError } from 'rxjs'
import { Router } from '@angular/router'
import { environment } from '../../../environments/environment.development'
import { HttpErrorResponse } from '@angular/common/http'

class HttpStrategyMock {
  execute = jasmine.createSpy('execute')
}

describe('ApiService', () => {
  let service: ApiService
  let routerSpy: jasmine.SpyObj<Router>
  let httpStrategyMock: HttpStrategyMock

  beforeEach(() => {
    routerSpy = jasmine.createSpyObj<Router>('Router', ['navigate'])
    httpStrategyMock = new HttpStrategyMock()

    TestBed.configureTestingModule(
      {providers: [
        ApiService,
        {
          provide: Router,
          useValue: routerSpy,
        },
        {
          provide: HttpStrategyMock,
          useValue: httpStrategyMock,
        },
      ]}
    )
    service = TestBed.inject(ApiService)
  })

  it('should be created', () => {
    expect(service).toBeTruthy()
  })

  it('should format URL correctly', () => {
    const baseUrl = environment.baseUrl
    const sufixUrl = '/test-endpoint'
    const expectedUrl = baseUrl + sufixUrl

    const formattedUrl = service['formatUrl'](sufixUrl)
    expect(formattedUrl).toBe(expectedUrl)
  })

  it('should handle 401 error by navigating to /login', () => {
    httpStrategyMock.execute.and.returnValue(
      throwError(() => new HttpErrorResponse({ status: 401 }))
    )

    service.execute(HttpStrategyMock, '/test-endpoint').subscribe({
      error: (error) => {
        expect(error.message).toBe('Falha ao carregar os dados.')
        expect(routerSpy.navigate).toHaveBeenCalledWith(['/login'])
      },
    })
  })
})
