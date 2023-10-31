from reportlab.pdfgen import canvas
import os
import pandas as pd
import glob
import qrcode
from PIL import ImageDraw, ImageFont

class QrGenerator:

    _width=794 
    _height=1123

    QrSize=0
    imgSize=0

    #Create new Page or add Page to existing pdf
    def createPDF(columnName,inputList):
        """
        createPage creates a new PDF file or adds a page to the existing PDF

        :string columnName: Name for the PDF file
        :list inputList: list of QR Code items
        """
        #Check if pdf file exists
        path = 'Output/page_{0}.pdf'.format(columnName)
        pathQr = './QrCode'

        if os.path.exists(path):            
            os.remove(path)

        
        can = canvas.Canvas(path,)
        firstRowfull = False
        offsetY = 0
        offsetX = 0
        checkY = 0
        checkX = 0

        for item in inputList:
            if not firstRowfull:
                can.drawImage("QrCode/qrcode_{0}.png".format(item),x=0,y=0+offsetY,width=QrGenerator.QrSize,height=QrGenerator.QrSize,showBoundary=True)
                offsetY += QrGenerator.QrSize
                checkY += QrGenerator.imgSize
            if firstRowfull:
                can.drawImage("QrCode/qrcode_{0}.png".format(item),x=0+offsetX,y=0+offsetY,width=QrGenerator.QrSize,height=QrGenerator.QrSize,showBoundary=True)
                offsetY += QrGenerator.QrSize
                checkY += QrGenerator.imgSize
            
            if checkY + QrGenerator.imgSize > QrGenerator._height and not item == inputList[-1]:
                checkX += QrGenerator.imgSize
                #Check if right side is full
                if checkX + QrGenerator.imgSize > QrGenerator._width:
                    can.showPage()
                    firstRowfull = False
                    checkX = 0
                    checkY = 0
                    offsetX = 0
                    offsetY = 0

                else:
                    firstRowfull = True
                    offsetX += QrGenerator.QrSize
                    checkY = 0
                    offsetY = 0
     
        can.save()
        QrGenerator.delete_files_in_directory(pathQr)
    
    #Helper function to set size of QRCode
    def mmtoPixel(mm):
        """
        mmtoPixel is a helper function to transfer mm to Pixel

        :int mm: millimeter to change to px
        """

        size = mm / 0.2645833333
        round(size)
        QrGenerator.QrSize=size
        QrGenerator.imgSize=size*1.33
        return size
    """
    Deletes all generated QR_Codes
    """   
    def delete_files_in_directory(directory_path):
        try:
            files = os.listdir(directory_path)
            for file in files:
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        except OSError:
            print("Ein Fehler ist aufgetreten die QR Code Bilder zu löschen. \n Bitte im Pfad ./QrCode/ manuell löschen.")
    
    def createQRCode(inputList):
        """
        createQrCode generates every item into a QR Code png as qrcode_{item}.png

        :list inputList: a list with items to generate as a QR Code
        """
        

        for input in inputList: 
            saveLocation = "QrCode/qrcode_{0}.png".format(str(input))
            width, height =(240,240)
            fontsize = 24
            font = ImageFont.truetype("Fonts/arial.ttf", fontsize)

            img = qrcode.make(input)
            draw = ImageDraw.Draw(img)

            _,_,w,h=draw.textbbox((0,0), str(input), font=font)
            
            draw.text((((width-w/2)-90), ((height-h)/2)-105),str(input),font=font)
            img.save(saveLocation)

runningProg=True   
while(runningProg):
    inputCheckNum = True
    inputcheckCol = True

    minSize=5
    maxSize=15

    csvListe=glob.glob("./Input/*.csv")

    #Check if there is no csv file in input
    if len(csvListe)<1:
        print("Bitte eine csv Datei in den Inputordner ablegen.")
        exit()
    #Check if there are more than one csv file in input

    if len(csvListe) > 1:
        print("Bitte nur eine csv Datei im Inputordner ablegen.")
        exit()

    #read csv into a dataframe
    for f in csvListe:
        data = pd.read_csv(f)

    #Check for empty entry in column
    if data.isnull().values.any():
        print("Leerer Eintrag entdeckt, bitte löschen!")
        exit()

    #Check from User which Column he wants to pick 
    while(inputcheckCol):
        try:
            print("Welche Spalte soll zu QR Codes generiert werden? \nFolgende liegen zur Auswahl:")
            for dataEntry in data.columns:
                print(dataEntry+", ",end="")
            columnName = str(input("\n"))

            if columnName in data.columns:
                inputcheckCol = False
            else:
                print("Diese Spalte existiert nicht")
        except:
            print("Diese Spalte existiert nicht")

    while(inputCheckNum):
        try:
            size = int(input("Welche Größe soll der QR Code haben? (5cm - 15cm) Bitte nur ganze Zahlen.\n"))

            if minSize <= size <= maxSize:
                inputCheckNum = False
            else:
                print("Das ist keine zugelassene Größe.")
        except:
            print("Das ist keine Korrekte Zahl")

    size*=10

    QrGenerator.createQRCode(data.eval(columnName).to_list())
    QrGenerator.mmtoPixel(size)
    QrGenerator.createPDF(columnName,data.eval(columnName).to_list())
    print("PDF abgespeichert im Ordner Output unter page_{0}.pdf".format(columnName))