import { Component } from '@angular/core'
import { MainPanelComponent } from './layout/main-panel/main-panel.component'

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MainPanelComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'frontend'
}
