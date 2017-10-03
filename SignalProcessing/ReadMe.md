# Signal Processing


### Andrea's R script:


    # series -> time series of EEG data
    # sampling -> s rate
    # length -> length of the moving window in seconds
    # sliding -> proportion of the window that is unique to each window
    #            (i.e., 1 - sliding = overlap)
    # hamming -> whether to apply a hamming window or not
    # x -> gyro X
    # y -> gyro Y
    # blink -> binary series, 1 = blink
    # quality -> discretized impedences, 5 = best, 1 = worst, 0 = NA
    #
    spectral_analysis <- function(series, sampling=128, length=2,
                                  sliding=0.75, hamming=T, x=NULL, y=NULL,
                                  blink=NULL, quality=NULL) {
            # Detrend linear shifts of the data.
            model <- lm(series ~ seq(1, length(series)))
            series <- (series - predict(model))
            
            # Remove motion components
            if (!is.null(x) & !is.null(y)) {
                    model <- lm(series ~ x + y)
                    series <- (series - predict(model))
            }
            
            # If no blink data is available,
            # create a "no-blink" fictitious series
            if (is.null(blink)) {
                    blink <- rep(0, length(series))
            }
            
            # If no quality data is available,
            # Create a fictitious "optimal quality" series
            if (is.null(quality)) {
                    quality <- rep(5, length(series))
            }
            
            # divide series into OL blocks of WINDOW samples, with
            # overlap of OVERLAP.
            
            ol = length * sliding
            #n = floor(length(series)/ (sampling * 2))
            n = 0
            size = sampling * (length * sliding)
            window = sampling * length
            spectrum_len <- (sampling * length)/2
            result <- rep(0, spectrum_len)
            
            # Cleanup procedures
            m <- mean(series)
            sd <- sd(series)
    
            # Identify reasonable boundaries.
            upper <- m + 3 * sd
            lower <- m - 3 * sd
            for (i in seq(1, length(series) - window, size)) {
                    sub <- series[i : (i + window - 1)]
                    bsub <- blink[i : (i + window - 1)]
                    qsub <- quality[i : (i + window - 1)]
                    if (length(sub[sub < lower | sub > upper]) == 0
                        & length(bsub[bsub > 0.5]) == 0
                        & min(qsub) > 1) {
                            n <- (n+1)
                            if (hamming) {
                                    sub <- sub * hamming.window(length(sub))
                            }
                            partial <- Re(fft(sub))^2
                            partial <- partial[1:spectrum_len]
                            result <- (result + partial)
                            #print(c(length(sub), result))
                    } else {
                            # Does nothing, really
                    }
            }
            # Average across the number of blocks
            result <- (result / n)
            
            result <- log(result)
            
            struct = list("Samples"=n,
                          "Freq"=seq(1/length, sampling/2, 1/length),
                          "Spectrum"=result,
                          "Sampling"=sampling,
                          "Quality"=quality,
                           "Blink"=blink,
    }
    

## Steven's matlab code


    marked = []; %make the "marked" array for future storage of bad channels
    a = 40; %This represents the starting maximum voltage's absolute value
    loops = 0;
    
    
    EEG = pop_select( EEG,'nochannel',31);
    
    %This is the first pass at rejection.
    EEG = pop_eegthresh(EEG,1,[1] ,(-20),(20),(EEG.xmin),(EEG.xmax),0,0);
    ratio2 = sum(EEG.reject(1).rejthresh)/EEG.trials
    
    %Here, we want to push the voltage absolutes to whatever point will
    %lead to less than 40 percent of the data being rejected, if they are used
    
    %
    maxcut = .1 %this is the is the maximum percent of data you are willing to cut out.
    
    while ratio2 > maxcut || loops < 20
        EEG = pop_eegthresh(EEG,1,[1] ,(-a),(a),(EEG.xmin),(EEG.xmax),0,0);
        ratio2 = sum(EEG.reject(1).rejthresh)/EEG.trials
        if ratio2 < maxcut
            %a = a - 2;
            break
        end
        if loops > 20 %If the number of cycles reaches 20 before the rejection ratio sinks below the maxcut, then the loop is broken.
            break
        end
        a = a + 5; %We go forward in steps of 5 uV.  More precise measures are possible if you use a smaller number here, but it will take more time.
        loops = loops+1;
    end
    %
    
    
    %Now to reject the bad epochs.  Technically you must screen them beforehand.
    EEG = pop_eegthresh(EEG,1,['1:(EEG.nbchan)'] ,num2str(-a),num2str(a),num2str(EEG.xmin),num2str(EEG.xmax),0,1);
    
    disp(strcat('the final voltage threshold value is: ', int2str(a)))