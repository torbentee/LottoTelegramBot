import {
  getUsersWhoShouldBeNotified,
  messageSent,
  setLottojackpot,
} from "../db";
import { sendMessage } from "./telegram";

const url = "https://www.lotto.de/api/stats/entities.lotto/last";

export async function fetchLottoJackpot() {
  const response = await fetch(url);
  const body = await response.json();
  return body as { jackpotNew: number; drawDate: string };
}

export async function pollLottojackpot() {
  console.log("Poll Lottojackpot");
  const response = await fetchLottoJackpot();
  const jackpot = response.jackpotNew;
  if (!jackpot) {
    return null;
  }

  const users = getUsersWhoShouldBeNotified(jackpot, "lottojackpot");

  await Promise.all(
    users.map((user) =>
      sendMessage(user.id, `Current lotto jackpot is ${jackpot}`)
    )
  );
  await messageSent(users, jackpot, "lottoJackpotLastmessage");
  await setLottojackpot(jackpot);
}
