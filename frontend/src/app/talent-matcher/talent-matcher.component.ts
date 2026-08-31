import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

import { environment } from '../../environments/environment';

@Component({
  selector: 'app-talent-matcher',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './talent-matcher.component.html',
  styleUrls: ['./talent-matcher.component.css']
})
export class TalentMatcherComponent {
  // Upload State
  selectedFile: File | null = null;
  uploadStatus: 'idle' | 'uploading' | 'success' | 'error' = 'idle';
  uploadMessage = '';

  // Match State
  jobDescription = '';
  matchStatus: 'idle' | 'searching' | 'done' | 'error' = 'idle';
  matchResults: any = null;

  // Configuration depuis l'environnement
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  // --- LOGIQUE UPLOAD ---
  onFileSelected(event: any) {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.pdf')) {
      this.selectedFile = file;
    } else {
      alert("Veuillez sélectionner un fichier PDF.");
    }
  }

  uploadCV() {
    if (!this.selectedFile) return;

    this.uploadStatus = 'uploading';
    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.http.post<any>(`${this.apiUrl}/upload-cv`, formData).subscribe({
      next: (res) => {
        this.uploadStatus = 'success';
        this.uploadMessage = `Succès ! Secteur détecté : ${res.secteur_detecte}`;
        setTimeout(() => { this.uploadStatus = 'idle'; this.selectedFile = null; }, 5000);
      },
      error: (err) => {
        this.uploadStatus = 'error';
        this.uploadMessage = "Erreur lors de l'upload du CV.";
        console.error(err);
      }
    });
  }

  // --- LOGIQUE MATCHING ---
  matchOffer() {
    if (!this.jobDescription.trim()) return;

    this.matchStatus = 'searching';
    const payload = { description: this.jobDescription };

    this.http.post<any>(`${this.apiUrl}/match`, payload).subscribe({
      next: (res) => {
        this.matchStatus = 'done';
        this.matchResults = res;
      },
      error: (err) => {
        this.matchStatus = 'error';
        console.error(err);
      }
    });
  }
}
