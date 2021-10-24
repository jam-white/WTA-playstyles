from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# Open a Chrome webdriver to use
PATH = '/usr/local/bin/chromedriver'
service = Service(PATH)
driver = webdriver.Chrome(service=service)

# Headings
main_stats_headings = ['aces', 'double_faults', 'first_srv_pct_in', 'win_pct_first_srv', 'win_pct_second_srv',
                       'net_points_won', 'break_points_won', 'rec_pts_won', 'winners', 'unforced_errors',
                       'total_points_won']
serve_stats_headings = ['fastest_serve', 'avg_1st_serve', 'avg_2nd_serve']
rally_stats_headings = ['short_rallies_pts_won', 'medium_rallies_pts_won', 'long_rallies_pts_won',
                        'medium_rallies_pts_played', 'short_rallies_pts_played', 'long_rallies_pts_played']

# Open a csv file for writing results
filename = 'frenchopen_data.csv'
header = 'player,opponent,tournament,year,round,total_points_played,' + ','.join(main_stats_headings) + ',' + \
         ','.join(serve_stats_headings) + ',' + ','.join(rally_stats_headings) + '\n'
with open(filename, 'w') as f:
    f.write(header)
tournie_info = 'french_open,2021,'

### HERE FIX round_num and looping
# Loop through all of the matches
for i in range(127):   # There are 127 matches to loop through
    round_num = 1
    for j in range(num_matches):
        match_num = j+1
        #match_code = '2' + str(round_num) + str(match_num).zfill(2)
        #match_url = 'https://www.wimbledon.com/en_GB/scores/stats/' + match_code + '.html'
        match_url = 'https://www.rolandgarros.com/en-us/matches/2021/SD043'

        # Variables for player names and points played;
        # lists for holding the data for each player before writing to the csv file
        player1_name = ''
        player2_name = ''
        points_played = ''
        player1_stats = []
        player2_stats = []

        # Open a particular webpage
        driver.get(match_url)

        # Wait until the webpage loads (once it can find the stats header) and grab the player names
        # (Quits the driver if it times out or gets another error)
        try:
            statsheader_div = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'StatsHeader'))
            )

            # Grab player names and total points played
            player_names = driver.find_elements(By.CLASS_NAME, 'name')
            player1_name = player_names[0].get_attribute('innerText')
            player2_name = player_names[1].get_attribute('innerText')

        except TimeoutException:
            print('The page took too long to load.')
            driver.quit()

        # Grab stats from the main stats table for each player
        # (n.b. this grabs each number repeated twice, so just keep the odd indexes)
        player1_main_stats = driver.find_elements(By.CLASS_NAME, 'player1')[1::2]
        player2_main_stats = driver.find_elements(By.CLASS_NAME, 'player2')[1::2]
        for p1_stat, p2_stat in zip(player1_main_stats, player2_main_stats):
            player1_stats.append(p1_stat.get_attribute('innerText'))
            player2_stats.append(p2_stat.get_attribute('innerText'))

        # Calculate total point played by summing points own by player1 and by player2
        points_played = int(player1_stats[10]) + int(player2_stats[10])

        # Navigate through the other stats pages and grab the stats
        # Navigate to rally analysis
        rally_analysis_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'tabRallyAnalysis')))
        driver.execute_script("arguments[0].click();", rally_analysis_button)
        time.sleep(1)

        # Grab rally analysis stats
        player1_rally_stats = [driver.find_elements(By.CLASS_NAME, 'team1')[i] for i in [3,10,17]]
        player2_rally_stats = [driver.find_elements(By.CLASS_NAME, 'team2')[i] for i in [3,10,17]]
        for p1_stat, p2_stat in zip(player1_rally_stats, player2_rally_stats):
            player1_stats.append(p1_stat.get_attribute('innerText'))
            player2_stats.append(p2_stat.get_attribute('innerText'))
        # Sum points won by each player to get the total points played, according to rally length
        total_pts_by_rally_length = [str(int(i)+int(j)) for i,j in zip(player1_stats[-3:], player2_stats[-3:])]
        player1_stats.extend(total_pts_by_rally_length)
        player2_stats.extend(total_pts_by_rally_length)

        #Write results to csv file
        with open(filename, 'a') as f:
            f.write(player1_name + ',' + player2_name + ',' + tournie_info + str(round_num) + ',' + str(points_played) +
                    ',' + ','.join(player1_stats) + '\n')
            f.write(player2_name + ',' + player1_name + ',' + tournie_info + str(round_num) + ',' + str(points_played) +
                    ',' + ','.join(player2_stats) + '\n')

driver.quit()
