from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Open a Chrome webdriver to use
PATH = '/usr/local/bin/chromedriver'
service = Service(PATH)
driver = webdriver.Chrome(service=service)

# List of stats to grab
# (n.b.: these are all named <stat>_p1 or <stat>_p2 according to player)
main_stats_to_grab_by_ID = [
    'aces',
    'double_faults',
    'first_srv_pct_in',
    'win_pct_first_srv',
    'win_pct_second_srv',
    'net_points_won',
    'break_points_won',
    'rec_pts_won',
    'winners',
    'unforced_errors',
    'total_points_won',
    'distance_per_pt'
]

serve_stats_headings = ['avg_1st_serve', 'avg_2nd_serve', 'avg_serve_overall', 'fastest_1st_serve', 'fastest_2nd_serve']
return_stats_headings = ['return_winners']
rally_stats_headings = ['approach_winners', 'approach_forced_errors', 'approach_unforced_errors', 'drop_shot_winners',
                        'drop_shot forced_errors', 'drop_shot unforced_errors', 'ground_stroke_winners',
                        'ground_stroke_forced_errors', 'ground_stroke_unforced_errors', 'lob_winners',
                        'lob_forced_errors', 'lob_unforced_errors', 'overhead_winners', 'overhead_forced_errors',
                        'overhead_unforced_errors', 'passing_winners', 'passing_forced_errors',
                        'passing_unforced_errors', 'volley_winners', 'volley_forced_errors', 'volley_unforced_errors']

# Open a csv file for writing results
filename = 'wimbledon_data.csv'
header = 'player,opponent,tournament,year,round,total_points_played,' + ','.join(main_stats_to_grab_by_ID) + ',' + \
         ','.join(serve_stats_headings) + ',' + ','.join(return_stats_headings) + ',' + \
         ','.join(rally_stats_headings) + '\n'
with open(filename, 'w') as f:
    f.write(header)
tournie_info = 'wimbledon,2021,'

# Loop through all of the matches
for i in range(7):   # There are 7 rounds to loop through
    round_num = i+1
    num_matches = int(64 * 1 / 2 ** i)   # Round 1 has 64 matches; each subsequent round has half as many
    for j in range(num_matches):
        match_num = j+1
        match_code = '2' + str(round_num) + str(match_num).zfill(2)
        match_url = 'https://www.wimbledon.com/en_GB/scores/stats/' + match_code + '.html'

        # Variables for player names and points played;
        # lists for holding the data for each player before writing to the csv file
        player1_name = ''
        player2_name = ''
        points_played = ''
        player1_stats = []
        player2_stats = []

        # Open a particular webpage
        driver.get(match_url)

        # Wait until the webpage loads (once it can find player1) and grab the player names
        # (Quits the driver if it times out or gets another error)
        try:
            player1_div = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'player1'))
            )

            # Grab player names and total points played
            # (n.b. player1 is stored as team 1, player 1 and player2 is stored as team 2, player 1)
            player_names = driver.find_elements(By.CLASS_NAME, 'player1')
            player1_name = player_names[0].get_attribute('innerText')
            player2_name = player_names[1].get_attribute('innerText')
            points_played = int(driver.find_element(By.ID, 'total_points_won_p1').get_attribute('innerText')) + \
                int(driver.find_element(By.ID, 'total_points_won_p2').get_attribute('innerText'))

        except TimeoutException:
            print('The page took too long to load.')
            driver.quit()

        # Grab stats that have straightforward IDs
        for stat in main_stats_to_grab_by_ID:
            p1_stat = driver.find_element(By.ID, stat + '_p1').get_attribute('innerText')
            p2_stat = driver.find_element(By.ID, stat + '_p2').get_attribute('innerText')
            player1_stats.append(p1_stat)
            player2_stats.append(p2_stat)

        # Navigate through the other stats pages and grab the stats
        # Navigate to serve stats
        stats_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/section/div[4]/div[2]/div[2]/span[2]/a[1]')))
        driver.execute_script("arguments[0].click();", stats_button)

        full_stats_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/section/'
                                                  'div[4]/div[2]/div[3]/div[2]/div[1]/section/div[3]/a')))
        driver.execute_script("arguments[0].click();", full_stats_button)

        serve_stats_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/section/div[4]/'
                                                  'div[2]/div[3]/div/div[1]/section/div[2]/ul/li[2]/a/span')))
        driver.execute_script("arguments[0].click();", serve_stats_button)

        # Grab serve stats
        serve_table = driver.find_element(By.CLASS_NAME, 'serve')
        serve_data = [x.get_attribute('innerText') for x in serve_table.find_elements(By.CLASS_NAME, 'stats-data')]
        serve_data = ['0' if x == '-' else x for x in serve_data]
        player1_stats.extend([serve_data[0], serve_data[1], serve_data[2], serve_data[6], serve_data[7]])
        player2_stats.extend([serve_data[3], serve_data[4], serve_data[5], serve_data[9], serve_data[10]])

        # Navigate to return stats
        return_stats_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/section/div[4]/'
                                                  'div[2]/div[3]/div/div[1]/section/div[2]/ul/li[3]/a/span')))
        driver.execute_script("arguments[0].click();", return_stats_button)

        # Grab return stats
        return_table = driver.find_element(By.CLASS_NAME, 'return')
        return_data = [x.get_attribute('innerText') for x in return_table.find_elements(By.CLASS_NAME, 'stats-data')]
        player1_stats.extend([return_data[2]])
        player2_stats.extend([return_data[5]])

        # Navigate to rally stats (some of these are disabled, so check that first)
        rally_stats_container = driver.find_element(By.XPATH,'// *[ @ id = "root"] / div / section / div[4] / div[2] / '
                                                             'div[3] / div / div[1] / section / div[2] / ul / li[4]')
        # If rally stats are not disabled, fill the player data with 'na'
        if 'disabled' in rally_stats_container.get_attribute('class'):
            player1_stats.extend(['na'] * 21)
            player2_stats.extend(['na'] * 21)

        # Otherwise, continue to navigate there and grab the data
        else:
            rally_stats_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="root"]/div/section/div[4]/'
                                                      'div[2]/div[3]/div/div[1]/section/div[2]/ul/li[4]/a/span')))
            driver.execute_script("arguments[0].click();", rally_stats_button)

            # Grab rally stats
            rally_table = driver.find_element(By.CLASS_NAME, 'rally')
            rally_data = [x.get_attribute('innerText') for x in rally_table.find_elements(By.CLASS_NAME, 'stats-data')]
            rally_data = [0 if x == '-' else int(x) for x in rally_data]
            # Sum FH and BH numbers from the table and add to relevant player lists
            for row in range(7):
                for col in range(3):
                    player1_stats.append(str(rally_data[(col*2)+(row*12)] + rally_data[(col*2+1)+(row*12)]))
                    player2_stats.append(str(rally_data[(col*2+6)+(row*12)] + rally_data[(col*2+7)+(row*12)]))

        # Write results to csv file
        with open(filename, 'a') as f:
            f.write(player1_name + ',' + player2_name + ',' + tournie_info + str(round_num) + ',' + str(points_played) +
                    ',' + ','.join(player1_stats) + '\n')
            f.write(player2_name + ',' + player1_name + ',' + tournie_info + str(round_num) + ',' + str(points_played) +
                    ',' + ','.join(player2_stats) + '\n')

driver.quit()
