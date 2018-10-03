/***********CODE FINAL DU BINOME 3 SERIE 6a 2BA PROJET ELECTRONIQUE APPLIQUEE*************
 Réalisé par: EL BAKKOURY YASSINE et EL HADDADI YASSINE
 Date: Mai 2018

 Sources: 
    LCD: https://www.arduino.cc/en/Tutorial/LiquidCrystalDisplay
         https://www.dropbox.com/s/fp51e82pgwxji6f/Code%20Afficheur.pdf
    LM35: https://www.carnetdumaker.net/articles/mesurer-une-temperature-avec-un-capteur-lm35-et-une-carte-arduino-genuino/
    Ultra-Son: https://www.hackster.io/ammaratef45/detecting-obstacles-and-warning-arduino-and-ultrasonic-13e5ea
    Buzzer: http://www.ardumotive.com/how-to-use-a-buzzer-en.html
    MAX7219 (+Matrice Led): http://plaisirarduino.fr/max-7219/  ou http://plaisirarduino.fr/telechargement-page_download/# TELECHARGER MAX7219. 
    Plusieurs codes s'y trouvent. ["..\Code sources MAX7219\Afficheur_Matrice\LedControle_matrice\LedControle_Led_matrice"] 
    Librairies LedControl.h : https://www.arduinolibraries.info/libraries/led-control TELECHARGER 
    Libraries LiquidCrystal.h : https://www.arduinolibraries.info/libraries/liquid-crystal TELECHARGER
ATTENTION, il est impératif de télécharger les libraries et de les placer dans le dossier Librarie qui accompagne le programme
Arduino pour faire marcher les #include. Il n'est pas nécessaire si le code fonctionne, sinon le problème pourrait provenir
d'une librarie manquante. 
*/


#include <LiquidCrystal.h> //Généralement fournie dans le programme, sinon il faut télécharger la librairie.
#include "LedControl.h" //La librarie doit être installée préalablement.
LedControl lc=LedControl(11,13,10,1);  
const int trigPin = 7;  
const int echoPin = 6;  
const int buzzPin = 8;

const int rs = 12, en = 9, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

int i=0, a=0;
float reft, indic ;
int t;
long duree, duree2;   
int distance;
int distance2; 
 
 
void setup() {
pinMode(trigPin, OUTPUT); 
pinMode(echoPin, INPUT);  
pinMode(buzzPin, OUTPUT);
Serial.begin(9600);
lcd.begin(16, 2); 
lc.shutdown(0,true);//Matrice Led éteinte.
lc.setIntensity(0,8);//Définit la luminosité.
lc.clearDisplay(0);//Efface la mémoire du MAX7219.
lc.setScanLimit(0, 8);//Définition le nombre de lignes à afficher.
}
 
void loop() {
  //Provoque un bip à chaque boucle pour prévenir que le système n'a rien détecté et est en cours de fonctionnement.
  tone(buzzPin,600);
  delay(1);
  noTone(buzzPin);
  
  //Lance la lecture de l'ultra-son.
  digitalWrite(trigPin, LOW);
  delayMicroseconds(5);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  duree = pulseIn(echoPin, HIGH);
  distance = duree*0.034/2;
  
  //Affiche la distance lue de l'ultra-son dans le moniteur série.
  Serial.print("Distance : ");
  Serial.print(distance);
  Serial.println("cm.");
  
  //Système de sécurité en cas de changement de distance.
  //NB: le système consiste en un couvercle qui protège un objet précieux. Une fois le couvercle retiré,
  //cela provoque une alarme.
  if (distance >=12){
    int s=0;
    while (s<15){//Nécessite 15 intervales pour que l'alarme cesse.
      Serial.println("ALERTE! ALERTE! MOUVEMENT SUSPECT! ALERTE! ALERTE!");
      tone(buzzPin, 1600); //Alarme sonore, active buzzer.
      delay(200);
      tone(buzzPin, 500);
      delay(10);
      lcd.display();
      lcd.setCursor(0,0);
      lcd.print("ALERTE!  ALERTE!");
      lcd.setCursor(0,1);
      lcd.print("   !MOUVEMENT! ");
      
      //Lance le clignotement de la matrice.
      lc.shutdown(0,false);//Allume la matrice.
      for (int row=0; row<8; row++){
        for (int col=0; col<8; col++){
          lc.setLed(0,col,row,true); //Allumer les leds en lignes et en colonnes.
          delay(1);}}
      for (int row=0; row<8; row++){
        for (int col=0; col<8; col++){
          lc.setLed(0,col,row,false); //Eteint les leds en lignes et en colonnes.
          delay(1);
          }
        }lc.shutdown(0,true);
      s=s+1;//Avance la boucle jusqu'à éteindre l'alarme.
    }
    lc.shutdown(0,true);//Eteint la matrice.
    lcd.clear();//Nettoie le lcd après la fin de l'alarme.
  }
  else {
    noTone(buzzPin);//Permet d'éteindre le buzzer après chaque boucle.
    }
  lcd.clear(); 

  //  Lance la lecture de température.
  int valeur_brute = analogRead(A0);
  float temperature_celcius = valeur_brute * (5.0 / 1023.0 * 100.0);
  lcd.setCursor(0,0);
  lcd.print("Lecture en cours");
  lcd.setCursor(0,1);
  lcd.print("Temp: ");
  lcd.print(temperature_celcius);
  lcd.print("C");
  lcd.display();
  delay(250);
  Serial.print("Température : ");
  Serial.print(temperature_celcius);
  Serial.println("°C.");
  
  
  
  i=i+1; //Permet d'enregistrer une première référence de température dans "reft" après 10 intervales de temps 
  //puis une autre référence tous les 50 intervales.
  if (i>10) {
    reft=temperature_celcius;
    i=-40;
    }
  indic = reft - temperature_celcius; //Indique la variation de température par rapport à la référence.

  if ( reft != NULL){//Permet de démarrer l'affichage de la donnée Variation dans le Moniteur série après la première référence.
    //Code semblable à l'alerte Distance.
    Serial.print("Variation : ");
    Serial.print(indic);
    Serial.println("°C.");
    if (indic >2 || indic<-2){//Si l'indicateur est trop important, lance une alerte.
      int t=0;
      while(t<5){//Nécessite 5 intervales pour que l'alerte cesse. 
        duree2 = pulseIn(echoPin, HIGH);
        distance2 = duree*0.034/2;
        if ( distance2 >=12){ //Si en plus de la variation de température, il y a un mouvement.
          lcd.clear();
          int u=0;
          while (u<10){//Cas clair d'intrusion dans le système.
            //Nécessite 10 intervales supplémentaires dans chacun des 5 intervales pour que l'alarme cesse.
            Serial.println("ALERTE! ALERTE! MOUVEMENT SUSPECT! ALERTE! ALERTE!");
            Serial.println("ALERTE! VARIATION IMPORTANTE DE TEMPERATURE! ALERTE!");
            tone(buzzPin, 1500); 
            delay(200);
            tone(buzzPin, 600);
            delay(200);
            lcd.display();
            lcd.setCursor(0,0);
            lcd.print("VARIATION TEMP!");
            lcd.setCursor(0,1);
            lcd.print(" !MOUVEMENT!");
            lc.shutdown(0,false);
            for (int row=0; row<8; row++){
              for (int col=0; col<8; col++){
                lc.setLed(0,col,row,true); //Allume les leds.
                delay(1);}}
            for (int row=0; row<8; row++){
              for (int col=0; col<8; col++){
                lc.setLed(0,col,row,false); //Eteint les leds.
                delay(1);
                }
              }
            u=u+1;
        }
        t=t+1;
        lc.shutdown(0,true);//Eteint la matrice.
      }
      else{
        lcd.clear();
        lcd.display();
        lcd.setCursor(0,0);
        lcd.print("ALERTE!  ALERTE!");
        lcd.setCursor(0,1);
        lcd.print("VARIATION TEMP!");
         Serial.println("ALERTE! VARIATION IMPORTANTE DE TEMPERATURE! ALERTE!");
         t=t+1;
         delay(400);
         lc.shutdown(0,false);
          for (int row=0; row<8; row++){
            for (int col=0; col<8; col++){
              lc.setLed(0,col,row,true); //Allume les leds.
              delay(1);}}
          for (int row=0; row<8; row++){
            for (int col=0; col<8; col++){
              lc.setLed(0,col,row,false); //Eteint les leds.
              delay(1);
              }
            }lc.shutdown(0,true);
          }
        lcd.clear(); 
        lc.shutdown(0,true);//Eteint la matrice.
      }
    }
  }
 Serial.println(" "); //Compose  une ligne vide dans le moniteur série.
 delay(600);//Relance la boucle après 600ms
 
 }
