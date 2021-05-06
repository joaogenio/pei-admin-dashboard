function [bHD b4K]= simulator2(lambda,p,n,S,W,R,fname)
    %lambda = request arrival rate (in requests per hour)
    %p      = percentage of requests for 4K movies (in %)
    %n      = number of servers
    %S      = interface capacity of each server (in Mbps)
    %W      = resource reservation for 4K movies (in Mbps)
    %R      = stop simulation on ARRIVAL no. R
    %fname  = filename with the duration of each movie
    
    invlambda=60/lambda;     %average time between requests (in minutes)
    invmiu= load(fname);     %duration (in minutes) of each movie
    Nmovies= length(invmiu); % number of movies
    C = n*S;                 %Internet connection capacity (in Mbps)
    
    %Events definition:
    ARRIVAL = 0;            %movie request
    DEPARTURE_HD = 1;     %termination of a HD movie transmission
    DEPARTURE_4K = 2; %termination of a 4K movie transmission
    %State variables initialization:
    STATE = zeros(1, n);
    STATE_HD = 0;
    %Statistical counters initialization:
    NARRIVALS = 0;
    REQUESTS_HD = 0;
    REQUESTS_4K = 0;
    BLOCKED_HD = 0;
    BLOCKED_4K = 0;
    %Simulation initial List of Events:
    [Min, Idx] = min(STATE);
    EventList= [ARRIVAL exprnd(invlambda) Idx];
 
    while NARRIVALS < R
        event= EventList(1,1);
        Clock= EventList(1,2);
        OldIdx = EventList(1,3);
        EventList(1,:)= [];
        if event == ARRIVAL
            [Min, Idx] = min(STATE);
            EventList= [EventList; ARRIVAL Clock+exprnd(invlambda) Idx];
            NARRIVALS= NARRIVALS+1;
            
            if (rand(1) > p/100)
                REQUESTS_HD = REQUESTS_HD+1;
                if STATE_HD + 5 <= C-W && Min <= S-5
                    STATE_HD = STATE_HD+5;
                    STATE(Idx) = STATE(Idx)+5;
                    EventList= [EventList; DEPARTURE_HD Clock+invmiu(randi(Nmovies)) Idx];
                else
                    BLOCKED_HD = BLOCKED_HD+1;
                end
            else
                REQUESTS_4K = REQUESTS_4K+1;
                if STATE(Idx) + 25 <= C && Min <= S-25
                    STATE(Idx) = STATE(Idx)+25;
                    EventList= [EventList; DEPARTURE_4K Clock+invmiu(randi(Nmovies)) Idx];
                else
                    BLOCKED_4K = BLOCKED_4K+1;
                end
            end
        elseif event == DEPARTURE_HD
            STATE_HD = STATE_HD-5;
            STATE(OldIdx) = STATE(OldIdx)-5;
        else 
            STATE(OldIdx) = STATE(OldIdx)-25;
        end
        EventList= sortrows(EventList,2);
    end
    bHD = 100*BLOCKED_HD/REQUESTS_HD;    % blocking probability of HD in %
    b4K = 100*BLOCKED_4K/REQUESTS_4K;    % blocking probability of 4K in %
end