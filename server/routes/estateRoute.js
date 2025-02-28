const express = require("express");
const db = require("../db/db");
const router = express.Router();

/**
 * 특정 사용자의 모든 부동산 정보 조회
 */
router.get("/:userId", (req, res) => {
    const userId = req.params.userId;
    db.query(
        "SELECT * FROM estates WHERE user_id = ?",
        [userId],
        (err, results) => {
            if (err) {
                console.error("❌ 데이터 조회 실패:", err);
                res.status(500).json({ error: "데이터 조회 실패" });
            } else {
                if (results.length === 0) {
                    res.status(404).json({ message: "데이터가 없습니다" });
                } else {
                    res.json(results);
                }
            }
        }
    );
});

/**
 * 새 부동산 정보 추가
 */
router.post("/", (req, res) => {
    const {
        user_id,
        contract_code,
        contract_date,
        name,
        subtitle,
        is_owned,
        is_leased,
        is_renting,
        price,
        rent,
        security_deposit,
        my_deposit,
        square,
        image_asset,
        price_change_rate,
        is_foreclosing,
        late_payments
    } = req.body;

    db.query(
        "INSERT INTO estates (user_id, contract_code, contract_date ,name, subtitle, is_owned, is_leased, is_renting, price, rent, security_deposit, my_deposit, square, image_asset, price_change_rate, is_foreclosing, late_payments) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [user_id, contract_code, contract_date, name, subtitle, is_owned, is_leased, is_renting, price, rent, security_deposit, my_deposit, square, image_asset, price_change_rate, is_foreclosing, late_payments],
        (err, result) => {
            if (err) {
                console.error("❌ 데이터 추가 실패:", err);
                res.status(500).json({ error: "데이터 추가 실패" });
            } else {
                res.json({ message: "부동산 정보 추가 성공", id: result.insertId });
            }
        }
    );
});

/**
 * 특정 부동산 정보 업데이트
 */
router.patch("/:userId/:code", (req, res) => {
    const user_id = req.params.userId;
    const code = req.params.code;

    // req.body에서 필요한 데이터 추출
    const {
        is_leased,
        my_deposit,
        is_foreclosing,
        late_payments
    } = req.body;

    console.log("🔍 요청된 데이터:", req.body);

    // 업데이트할 데이터 확인
    if (!is_leased && !my_deposit && !is_foreclosing && !late_payments) {
        return res.status(400).json({ error: "업데이트할 데이터가 없습니다." });
    }

    // SQL 쿼리 및 데이터 배열
    const query = `UPDATE estates SET is_leased = ?, my_deposit = ?, is_foreclosing = ?, late_payments = ? WHERE contract_code = ? AND user_id = ?`;
    const values = [is_leased, my_deposit, is_foreclosing, late_payments, code, user_id];

    // 데이터베이스 업데이트 실행
    db.query(query, values, (err, result) => {
        if (err) {
            console.error("❌ 데이터 업데이트 실패:", err);
            return res.status(500).json({ error: "데이터 업데이트 실패" });
        }
        res.json({ message: "부동산 정보 업데이트 성공", affectedRows: result.affectedRows });
    });
});

/**
 * 특정 부동산 정보 삭제
 */
router.delete("/:userId/:code", (req, res) => {
    const user_id = req.params.userId;
    const code = req.params.code;
    //contract코드로 찾아서 수정하는 로직 추가
    db.query("DELETE FROM estates WHERE contract_code = ? AND user_id = ?", [code, user_id], (err, result) => {
        if (err) {
            console.error("❌ 데이터 삭제 실패:", err);
            res.status(500).json({ error: "데이터 삭제 실패" });
        } else {
            res.json({ message: "부동산 정보 삭제 성공" });
        }
    });
});

module.exports = router;
