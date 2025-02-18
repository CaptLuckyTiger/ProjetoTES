from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


class CertificateGenerator:
    def generate_certificate(self, image_path, text, output_path=None):
        raise NotImplementedError("O metodo não será subscrevido pela classe.")


class PILCertificateGenerator(CertificateGenerator):
    def generate_certificate(self, image_path, text, output_path=None):
        image = Image.open(image_path)

      
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 40) 

        
        text_position = (100, 100)
        draw.text(text_position, text, fill="black", font=font)

 
        if output_path:
            image.save(output_path)
            return output_path
        else:
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            buffer.seek(0)
            return buffer


class GenerateCertificateView(View):
    def post(self, request):
        image = request.FILES.get("image")
        text = request.POST.get("text")

        if not image or not text:
            return HttpResponse("Imagem ou texto não fornecido.", status=400)

   
        temp_image_path = f"/tmp/{image.name}"
        with open(temp_image_path, "wb") as f:
            for chunk in image.chunks():
                f.write(chunk)

     
        generator = PILCertificateGenerator()
        result = generator.generate_certificate(temp_image_path, text)

    
        response = HttpResponse(result, content_type="image/png")
        response["Content-Disposition"] = 'attachment; filename="certificate.png"'
        return response

    def get(self, request):
        return render(request, "generate_certificate.html")
