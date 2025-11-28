#define SENSOR_LOCAL 7
#define SENSOR_AWAY 8

bool prev_local = HIGH;
bool prev_away = HIGH;

void setup()
{
    Serial.begin(9600);
    pinMode(SENSOR_LOCAL, INPUT_PULLUP);  // Usa resistencias internas
    pinMode(SENSOR_AWAY, INPUT_PULLUP);
}

void loop()
{
    bool current_local = digitalRead(SENSOR_LOCAL);
    bool current_away = digitalRead(SENSOR_AWAY);

    // Detecta cuando se presiona el botón (flanco de HIGH a LOW)
    if (prev_local == HIGH && current_local == LOW)
    {
        Serial.println("A");  // Gol local
        delay(200);           // Debounce
    }

    if (prev_away == HIGH && current_away == LOW)
    {
        Serial.println("B");  // Gol visitante
        delay(200);           // Debounce
    }

    prev_local = current_local;
    prev_away = current_away;
}
