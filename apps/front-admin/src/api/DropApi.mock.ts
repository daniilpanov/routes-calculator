import { Drop } from "@/interfaces/Model/Drop";

export async function addDrop(drop: Drop) {
    return {
        status: "OK",
        new_drop: {
            "id": 121111,
            "company": {
                "id": 10,
                "name": "HUB",
            },
            "container": {
                "id": 6,
                "name": "20DC ≤ 24t",
                "size": 20,
                "type": "DC",
                "weight_from": 0,
                "weight_to": 24,
            },
            "sea_start_point": {
                "id": 4,
                "city": "Safiport",
                "country": "Turkey",
                "RU_city": "Сафипорт",
                "RU_country": "Турция",
            },
            "sea_end_point": {
                "id": 83,
                "city": "Vrangel Bay",
                "country": "Russia",
                "RU_city": "порт Врангель",
                "RU_country": "Россия",
            },
            "rail_start_point": {
                "id": 83,
                "city": "Vrangel Bay",
                "country": "Russia",
                "RU_city": "порт Врангель",
                "RU_country": "Россия",
            },
            "rail_end_point": {
                "id": 88,
                "city": "Novosibirsk",
                "country": "Russia",
                "RU_city": "Новосибирск",
                "RU_country": "Россия",
            },
            "start_date": 1751328000,
            "end_date": 1767139200,
            "price": 666,
            "currency": "USD",
        },
    };
}
