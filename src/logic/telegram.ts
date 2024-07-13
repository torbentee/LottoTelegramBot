import { Telegraf } from "telegraf";
import { getFullConfig, insert, start } from "../db";
import { fetchLottoJackpot } from "./lotto";
import { fetchEuroJackpot } from "./euro";
import {
  getMessageparameter,
  hasMessageParameter,
  toBeautyString,
} from "../util";
import { sleep } from "bun";

const bot = new Telegraf(process.env.BOT_TOKEN ?? "");

export function init() {
  bot.start(async (ctx) => {
    const { id } = ctx.chat;
    console.log("start new chat", id);
    await start(id);

    return ctx.reply("Ok! Let's get a notification for _Eurojackpot_ /help");
  });
  bot.help((ctx) =>
    ctx.reply(
      "/start - register to use the Lotto News Bot\n/help - show this help\n/eurojackpot -\n/lottojackpot -\n/settings -"
    )
  );
  bot.command("settings", (ctx) => {
    const config = getFullConfig(ctx.chat.id);
    const configString = toBeautyString(config);

    ctx.reply(configString);
  });
  bot.command("eurojackpot", async (ctx) => {
    if (hasMessageParameter(ctx.message.text, "eurojackpot")) {
      const eurojackpotBottomBound = parseInt(
        getMessageparameter(ctx.message.text, "eurojackpot")
      );
      await insert({
        id: ctx.chat.id,
        timestamp: new Date().getTime(),
        eurojackpotBottomBound,
      });
      await sleep(400);
      return ctx.react("👍");
    } else {
      const response = await fetchEuroJackpot();
      const drawDate = new Date(response.drawDate).toDateString();
      const jackpot = response.jackpotNew;
      return ctx.reply(toBeautyString({ jackpot, drawDate }));
    }
  });
  bot.command("lottojackpot", async (ctx) => {
    if (hasMessageParameter(ctx.message.text, "lottojackpot")) {
      const lottojackpotBottomBound = parseInt(
        getMessageparameter(ctx.message.text, "lottojackpot")
      );
      await insert({
        id: ctx.chat.id,
        timestamp: new Date().getTime(),
        lottojackpotBottomBound,
      });
      await sleep(400);
      return ctx.react("👍");
    } else {
      const response = await fetchLottoJackpot();
      const drawDate = new Date(response.drawDate).toDateString();
      const jackpot = response.jackpotNew;
      return ctx.reply(toBeautyString({ jackpot, drawDate }));
    }
  });

  bot.launch();
  // Enable graceful stop
  process.once("SIGINT", () => bot.stop("SIGINT"));
  process.once("SIGTERM", () => bot.stop("SIGTERM"));
}

export async function sendMessage(chatId: number, message: string) {
  const response = await bot.telegram.sendMessage(chatId, message);
  return response;
}
