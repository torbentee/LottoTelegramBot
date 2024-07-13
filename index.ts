import { CronJob } from "cron";
import { init } from "./src/logic/telegram";
import { pollEurojackpot } from "./src/logic/euro";
import { pollLottojackpot } from "./src/logic/lotto";

init();
CronJob.from({
  cronTime: "* * * * *",
  onTick: () => {
    pollEurojackpot();
    pollLottojackpot();
  },
  start: true,
  timeZone: "Europe/Berlin",
});

console.log("Bot started");
