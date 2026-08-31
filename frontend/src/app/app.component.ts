import { Component } from '@angular/core';
import { TalentMatcherComponent } from './talent-matcher/talent-matcher.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [TalentMatcherComponent],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
}
