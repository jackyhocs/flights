# Skypath

Flight connection search engine: given an origin, destination, and date, finds all direct, 1-stop, and
2-stop itineraries and returns them sorted by total trip duration. Flask backend + React (Vite) frontend,
run together via `docker-compose up`.

## Run instructions
1. Pull this repo
2. run `docker-compose up` to spin up frontend and backend services
	* Backend is reachable at port 5000
	* Frontend is reachable at port 3000


### Testing
Backend
1. cd to `backend` folder
2. create and run a venv
3. install packages from requirements-dev.txt
4. run `python -m pytest tests/ -q`

Frontend
1. cd to `frontend` folder
2. run `npm install`
3. run `npm run test`

## API Contract

`GET /api/search?origin={AIRPORTCODE}&destination={AIRPORTCODE}&date={DATETIME}`

All three params are required. 

AIRPORTCODE = 3-letter IATA airport code, provided in frontend dropdown
DATETIME = valid ISO 8601 date time, provided via a widget on frontend

Frontend widgets add enforcement to having valid data to be passed to backend. 

However, backend is hardened against bad input in the event that the request is sent directly to the API. Returns `400 {"error": "..."}` for missing/malformed params, non-3-letter codes, an unknown airport code, `origin == destination`, or a bad date format that is not ISO 8601.

On success, returns `200` with a list of Itineraries sorted ascending by `totalDurationMinutes`. Each itinerary has `stops`, `totalDurationMinutes`,
`totalPrice`, a list of `segments` (flight number, airline, origin/destination, local departure/arrival
times, price, aircraft), and a list of `layovers` (airport, duration, and `domestic`/`international` type).


## Backend Overall Notes
* Flake8 is used for enforcing style and consistency. However, we can enforce code styling as one of the CI/CD steps instead, or have linting be an explicit step as part of the git push process.
* For constants, we currently have a static file that is checked into the repo that contains all the constants (i.e. max stops, etc). This being a file checked into the main repo is fine for a project but if this service scales and there are lengthy CI/CD processess/steps, we may instead want to have the config be checked into a separate repo to decouple the config with the code changes. For now since this is fine but this is a tradeoff to be made in the future.


### Data loader decisions and assumptions
Assumptions:
1. Data cleanliness: I have unit tests to check that the data provided is reasonably accurate to the json file provided. This loader does not anticipate for cases where, for example, if certain flights have airports with different casing. I have added guards for scenarios around missing/malformed required fields, invalid/unparseable dates, impossible flights (going back in time), and empty datasets, but I believe that having valid cases and data will be more interesting instead of having pedantic verification/tests.  

Decisions/Improvements:
1. In the happy case unit tests, we load the full dataset directly from the json file. This is a decision made right now to ensure tests are hermetic and isolated. This is at the cost of time to load/parse the json files, but because the dataset file is small, this is not be a concern right now. If datasets get bigger, then we will revisit this based on what the requirements of the unit tests are.
2. In the edge case unit tests, instead of loading in the entire json file, we create temporary json fixtures with the invalid/custom flight and ensure that the data loader skips the exceptions without crashing. 
3. I have added a test case/restraint for uniqueness on the "flightNumber" key. Any two flights should not have the same flight number, in the event of a duplicate, only the first flight is loaded, the rest are logged as warning during json loading.
4. Flights `SP995`, `SP996`, and `SP998` have string-typed `price` fields (e.g. `"299"` instead of `299`) on app startup, the loader parses these to a float.
5. Flight `SP995` had a typo of "JKF", I have decided to rename this to the corrected version instead of throwing a warning and not logging this. We may want to throw a warning instead, but I currently prefer just making the change since this is a small dataset and having one more available flight may affect test cases.

### Search Algorithm decisions and assumptions
Assumptions:
1. Data loader's assumptions of clean data are enforced (i.e. no duplicate flights) - currently, we do not do any post-processing except a sort on the itinerary's duration. Also, for cost-oriented travellers, we may want to have a parameter for the sort key, as they may care more for optimizing cost, but that is outside the scope, as the spec mentions to sort by total travel time.

Decisions/Improvements:
1. Search algorithm - DFS over BFS:  Since we're currently not concerned with finding only the shortest flights, DFS will explore all the options up to the maximum configured 2 stops. We perform a sort once all the valid itineraries are generated. Complexity is a concern if this is a production environment because the complexity would be O(f^3), where f is the number of outbound flights at an airport. However, as a naive first approach, this currently works because the dataset is small. Realistically, we should not do this brute force approach for a production algorithm but because the flight set is constant and small, this is manageable for now but should not be used in a real setting. For some optimizations on a production algorithm, I would look more into Djikstra/A* algorithms to gather the "best" itineraries, as there would be real time and cost bounds that can be used as edge weights for computing/weighing the best itineraries. Additionally, another optimization would be to prune some flight candidates earlier on with time or cost-bounding instead of computing every single possibility exhaustively.
2. Datastore choice - Flights json in memory: Realistically we should never keep the datastores in memory if it's real data. However, since this is a small static dataset, this is fine for now but can/should be saved in a datastore in production. In that production example, here are some high level thoughts using CAP theorem. Partition tolerance is an assumption with scalable systems, so we have to decide between strong consistency and high availability. I believe that depending on the service, we can enforce the correct property depending on the context. For the checkout flow (out of scope), we should have strong consistency in the checkout flow to ensure that we do not accidentally double-book on a specific seat or sell a ticket for a flight that has been sold out. Conversely, high availability for the searching flow to provide the best user experience (low availability would be a nightmare customer experience and will easily sink satisfaction and conversion rate). With these two working in conjunction, in the unfortunate event of a user seeing a flight (high availability) but when they go to checkout, it has already been sold out, we would float an exception to the user and suggest other flights that are still available (strong consistency). This is product behaviour, so while this is my perspective from an engineer, it is entirely possible that we believe in different core principles. Furthermore, depending on local legal or regulatory laws, if we are contractually obligated to charge the price that users see from the site/algorithm, we may want to prioritize consistency to ensure that we are computing the right prices with available flights first over high availability, where the underlying flights may be already sold-out.



### Flask endpoint decisions and assumptions
Assumptions:
1. Traffic is valid: we do not have any auth right now so all traffic is processed, we can put in some auth to prevent bots or bad actors and to provide a level of rate-limiting. Not in scope, so we only return a 400 if the input is malformed as a backend guardrail against injection from frontend even if the user gets past frontend validations.
2. CORS: In production, allowing all origin in CORS is a huge security issue. However for ease of testing, I'm choosing to ease on this aspect. 

Decisions/Improvements:
1. Unwrapped/naked Exceptions: In production, we probably want to wrap the existing exceptions with traces/output to be logged for debugging purposes. For this task we do not log anything and we just return the `400` error code with a simple message indicating the reason behind the failed validation.
2. Dataload time: Currently we load and process the data at app startup instead of at query-time. This is so that if we have a poisoned pill/bad data loading, we will find out at the time that the service spins up instead of at request time. Also, having built the graph and processed the data before requests are served, we ensure that the requests are fast and users do not have to wait for the computing overhead.
3. Infra improvements: Currently with flask dev server, it is single threaded, so to handle more production traffic, we can use uWSGI or gunicorn. For proxying, load balancing and cache, I've used nginx previously so I would probably use that unless the team has something better built-in house or an existing solution.
4. Airport validations/lookup: Instead of having a backend endpoint that will return a list of valid endpoints, I have decided to have frontend and backend validation on the airport field. While we enforce that the user's input form contains only valid airports, we can choose to allow this to be a text box but that would require more validation. For the purposes of this demo/task, I've made it so it's the simplest.


## Frontend notes
* Apologies for the UX, I have chosen to use Material UI and FontAwesome icons, as that is what I have used previously for work and for school projects and am more comfortable with them. These can easily be replaced with in-house or other components or icon libraries.

Decisions/Improvements
1. Tooling: I used Vite as the build/development tool because it is lightweight and I do not need the control that Webpack offers at this time. 
2. Hardcoded list of airports: Instead of a text box, as I have outlined above, I have instead hardcoded a list of valid airports. In production, we can have this be a different experience with a text box that has auto-fill based on the input (users may type in the whole airport name instead of the airport code). This approach normalizes this behaviour and provides clear data to provide to the backend. First guardrail of user input, but we will perform validations on both backend and frontend to harden the service from bad inputs. We have already created a check in the frontend to prevent users from having the same airport Origin/Destination. Logically speaking, we should have a check for flights in the past, as trip-booking are for future trips, but for the sake of the data, we have ignored this.
3. Frontend verification/auth: Again, since we do not have any form of bot/spam guards, we will accept all requests. For rate limiting and other auth, we could add this and some hidden forms that the bots will fill out to prevent DDOS/spam.
4. Timezones: Each segment's departure and arrival times are shown in that airport's own local time (as returned by the backend), with a short timezone abbreviation appended (e.g. "8:30 AM PDT").
5. Error handling: As a personal choice, if there is an existing itinerary loaded on the screen. If the user enters an invalid O/D in the trip and attempts to search, we clear the existing itineraries and show the error code instead of only serving the error code with no frontend updates.
