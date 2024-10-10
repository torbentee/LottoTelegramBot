import { JSONFilePreset } from "lowdb/node";

export type Values = {
  id: number;
  timestamp: number;
  euroJackpotLastmessage?: number;
  lottoJackpotLastmessage?: number;
  eurojackpotBottomBound?: number;
  lottojackpotBottomBound?: number;
  start?: boolean;
}[];
type Global = {
  eurojackpot: { lastJackpot: number };
  lottojackpot: { lastJackpot: number };
};
type Database = { values: Values; global: Global };
type ArrayElement<ArrayType extends readonly unknown[]> =
  ArrayType extends readonly (infer ElementType)[] ? ElementType : never;

const db = await JSONFilePreset<Database>("db/db.json", {
  values: [],
  global: { eurojackpot: { lastJackpot: 0 }, lottojackpot: { lastJackpot: 0 } },
});

export function reduceUser(entries: Values): ArrayElement<Values> | null {
  const sortedEntries = entries.sort((a, b) => a.timestamp - b.timestamp);
  if (sortedEntries.length === 0) {
    return null;
  }
  return sortedEntries.reduce((prev, cur) => ({ ...prev, ...cur }));
}

export async function setEurojackpot(jackpot: number) {
  return db.update((prev) => (prev.global.eurojackpot.lastJackpot = jackpot));
}

export async function setLottojackpot(jackpot: number) {
  return db.update((prev) => (prev.global.lottojackpot.lastJackpot = jackpot));
}

export function processData(
  data: Values,
  id: number
): ArrayElement<Values> | null {
  if (!data || !Array.isArray(data)) {
    return null;
  }
  const listEntries = data.filter((value) => value.id === id);
  return reduceUser(listEntries);
}

export async function insert(data: ArrayElement<Values>) {
  return db.update((prev) => prev.values.push({ ...data }));
}

export function get(id: number) {
  const data = db.data.values;
  return processData(data, id);
}

export async function start(id: number) {
  const current = get(id);
  if (!current) {
    const timestamp = new Date().getTime();
    insert({ id, timestamp, start: true });
  }
}

export function getUsersWhoShouldBeNotified(
  jackpot: number,
  type: "eurojackpot" | "lottojackpot",
  database = db.data.values
): Values {
  function filterOfTime(value: ArrayElement<Values>): boolean {
    const chenged = hasJackpotChanged(jackpot, type);
    const notify = hasUserBeenNotifiedOfThisJackpot(jackpot, type, value);
    return chenged || notify;
  }

  const map = {
    eurojackpot: "euroJackpotLastmessage",
    lottojackpot: "lottoJackpotLastmessage",
  } as const;

  return getLatestState(database)
    .filter((value) => {
      const a = map[type];
      if (a === undefined) return true;
      const b = value[a];
      if (b === undefined) return true;
      return b !== jackpot;
    })
    .filter(filterOfTime);
}

export function getLatestState(db: Values) {
  if (!db || !Array.isArray(db)) return [];
  const intermediateObject = db
    .sort((a, b) => a.timestamp - b.timestamp)
    .reduce((prev, cur) => {
      const id = cur.id;
      return {
        ...prev,
        [id]: {
          ...prev[id],
          ...cur,
        },
      };
    }, {} as { [key: number]: ArrayElement<Values> });
  return Object.values(intermediateObject) as Values;
}

function hasJackpotChanged(
  jackpot: number,
  type: "eurojackpot" | "lottojackpot"
): boolean {
  return db.data.global[type].lastJackpot !== jackpot;
}

function hasUserBeenNotifiedOfThisJackpot(
  jackpot: number,
  type: "eurojackpot" | "lottojackpot",
  value: ArrayElement<Values>
): boolean {
  const map = {
    eurojackpot: "euroJackpotLastmessage",
    lottojackpot: "lottoJackpotLastmessage",
  } as const;
  return value[map[type]] !== jackpot;
}

export function getFullConfig(id: number) {
  return get(id);
}

export async function messageSent(
  users: Values,
  jackpot: number,
  type: "euroJackpotLastmessage" | "lottoJackpotLastmessage"
) {
  const newData = users.map((user) => ({
    id: user.id,
    [type]: jackpot,
    timestamp: new Date().getTime(),
  }));
  return db.update((prev) => prev.values.push(...newData));
}
