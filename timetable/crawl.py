from scrapy import cmdline

def run():
    cmdline.execute("scrapy crawl timetable".split())

if __name__ == "__main__":
    run()
