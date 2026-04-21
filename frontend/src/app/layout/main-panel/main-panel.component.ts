import { Component } from '@angular/core'
import { FontAwesomeModule } from '@fortawesome/angular-fontawesome'
import { faMagnifyingGlass, faSort } from '@fortawesome/free-solid-svg-icons'

@Component({
  selector: 'app-main-panel',
  standalone: true,
  imports: [FontAwesomeModule],
  templateUrl: './main-panel.component.html',
  styleUrl: './main-panel.component.scss',
})
export class MainPanelComponent {
  faSearch = faMagnifyingGlass
  faSort = faSort
}
