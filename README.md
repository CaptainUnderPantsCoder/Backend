# Backend
Backend for ProjectAura
START HERE

1. Put modele_chiffres.pkl and scaler.pkl inside the models folder.
2. Double-click setup_backend.bat once.
3. Double-click run_backend.bat whenever you want to start the backend.
4. Open http://127.0.0.1:8000 in your browser.
5. Open test_frontend.html and draw a digit to test the prediction.

Important:
- The image sent to /predict must be exactly 28 x 28 pixels.
- Pixel values must be between 0 and 255.
- White digit on black background.
- Do NOT divide the pixel values by 255 before using scaler.pkl.
