from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction as db_transaction

# Імпорти моделей
from apps.subscriptions.models import Subscription, Credit, Payment
from apps.core.models import Transaction, Category

class Command(BaseCommand):
    help = 'Автоматично створює транзакції та платежі. Можна вказати конкретного юзера.'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=int, help='ID користувача для обробки')

    def handle(self, *args, **options):
        now = timezone.now()
        today = now.date()
        current_year = today.year
        current_month = today.month

        target_user_id = options['user']

        # Створення/отримання категорії для кредитів
        cat_credits, _ = Category.objects.get_or_create(
            name="Кредити", 
            defaults={'icon': '🏦', 'color': 'warning'}
        )

        user_msg = f" (User ID: {target_user_id})" if target_user_id else " (ВСІ)"
        self.stdout.write(f"Запуск обробки платежів на {today}{user_msg}...")

        # ==========================================
        # 1. ОБРОБКА ПІДПИСОК
        # ==========================================
        sub_filters = {'is_active': True, 'next_payment_date': today}
        if target_user_id:
            sub_filters['user_id'] = target_user_id

        subscriptions = Subscription.objects.filter(**sub_filters)

        for sub in subscriptions:
            # --- ПЕРЕВІРКА 1: Чи вже платили цього місяця? ---
            already_paid = Payment.objects.filter(
                subscription=sub,
                created_at__year=current_year,
                created_at__month=current_month
            ).exists()

            if already_paid:
                self.stdout.write(self.style.WARNING(f"⚠️ Пропущено {sub.title}: Вже оплачено в цьому місяці"))
                continue
            # -------------------------------------------------

            try:
                transaction_category = Category.objects.get(name__iexact=sub.title)
            except Category.DoesNotExist:
                self.stdout.write(self.style.ERROR(
                    f"❌ ПОМИЛКА {sub.title}: Категорія '{sub.title}' не знайдена в базі! "
                    f"Створіть категорію з такою назвою."
                ))
                continue

            if not sub.from_asset:
                self.stdout.write(self.style.WARNING(f"Пропущено {sub.title}: немає рахунку"))
                continue

            if sub.from_asset.balance < sub.amount:
                self.stdout.write(self.style.ERROR(f"❌ ВІДХИЛЕНО {sub.title}: Немає коштів"))
                continue

            try:
                with db_transaction.atomic():
                    sub.from_asset.balance -= sub.amount
                    sub.from_asset.save()

                    new_transaction = Transaction.objects.create(
                        asset=sub.from_asset,
                        amount=sub.amount,
                        type='expense',
                        category=transaction_category, 
                        created_at=timezone.now(),
                        description=f"Автооплата підписки: {sub.title}"
                    )

                    Payment.objects.create(
                        transaction=new_transaction,
                        subscription=sub,
                        amount=sub.amount,
                        payment_type='subscription'
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ Оплачено: {sub.title} (Категорія: {transaction_category.name})"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Помилка {sub.title}: {e}"))


        # ==========================================
        # 2. ОБРОБКА КРЕДИТІВ
        # ==========================================
        credit_filters = {
            'is_active': True, 
            'payment_day': today.day, 
            'remaining_amount__gt': 0
        }
        if target_user_id:
            credit_filters['user_id'] = target_user_id

        credits = Credit.objects.filter(**credit_filters)

        for credit in credits:
            # --- ПЕРЕВІРКА 1: Чи вже платили цього місяця? ---
            already_paid = Payment.objects.filter(
                credit=credit,
                created_at__year=current_year,
                created_at__month=current_month
            ).exists()

            if already_paid:
                self.stdout.write(self.style.WARNING(f"⚠️ Пропущено {credit.name}: Вже оплачено в цьому місяці"))
                continue
            # -------------------------------------------------

            if not credit.from_asset:
                self.stdout.write(self.style.WARNING(f"Пропущено {credit.name}: немає рахунку"))
                continue
            
            amount_to_pay = credit.monthly_payment
            if credit.remaining_amount < amount_to_pay:
                amount_to_pay = credit.remaining_amount

            if credit.from_asset.balance < amount_to_pay:
                self.stdout.write(self.style.ERROR(f"❌ ВІДХИЛЕНО {credit.name}: Немає коштів"))
                continue

            try:
                with db_transaction.atomic():
                    credit.from_asset.balance -= amount_to_pay
                    credit.from_asset.save()

                    new_transaction = Transaction.objects.create(
                        asset=credit.from_asset,
                        amount=amount_to_pay,
                        type='expense',
                        category=cat_credits, 
                        created_at=timezone.now(),
                        description=f"Автооплата кредиту: {credit.name}"
                    )

                    Payment.objects.create(
                        transaction=new_transaction,
                        credit=credit,
                        amount=amount_to_pay,
                        payment_type='credit'
                    )
                    self.stdout.write(self.style.SUCCESS(f"✅ Оплачено: {credit.name}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Помилка {credit.name}: {e}"))

        self.stdout.write("--- Кінець обробки ---")