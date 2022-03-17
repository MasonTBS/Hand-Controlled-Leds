// Example 5 - Receive with start- and end-markers combined with parsing

const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

      // variables to hold the parsed data
char messageFromPC[numChars] = {0};
float rightSpeed = 0.0;
float leftSpeed = 0.0;

boolean newData = false;
int rightLedPin = 9;
int leftLedPin = 10;

//============

void setup() {
    Serial.begin(9600);
    Serial.println("This demo expects 3 pieces of data - text, an integer and a floating point value");
    Serial.println("Enter data in this style <HelloWorld, 12, 24.7>  ");
    Serial.println();
    pinMode(rightLedPin, OUTPUT);
    pinMode(leftLedPin, OUTPUT);

    digitalWrite(rightLedPin, HIGH);
    digitalWrite(leftLedPin, HIGH);
    delay(2000);
}

//============

void loop() {
    recvWithStartEndMarkers();
    if (newData == true) {
        strcpy(tempChars, receivedChars);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        parseData();
        showParsedData();
        newData = false;
    }
    led();
}

//============

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();
        
        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}

//============

void parseData() {      // split the data into its parts

    char * strtokIndx; // this is used by strtok() as an index
   // strtokIndx = strtok(tempChars,",");      // get the first part - the string
   // strcpy(messageFromPC, strtokIndx); // copy it to messageFromPC
 
    strtokIndx = strtok(tempChars, ","); // this continues where the previous call left off
    leftSpeed = atof(strtokIndx);     // convert this part to an integer

    strtokIndx = strtok(NULL, ",");
    rightSpeed = atof(strtokIndx);     // convert this part to a float

}

//============

void showParsedData() {
    //Serial.print("flaot1: ");
    //Serial.println(rightSpeed);
    //Serial.print("float2: ");
    //Serial.println(leftSpeed);
}

void led()
{
  analogWrite(rightLedPin, rightSpeed*255);
  analogWrite(leftLedPin, leftSpeed*255);
  delay(1);
}
